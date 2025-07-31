/* ***********************************************************************
//
//   Copyright (C) 2025 -- The 4D-STAR Collaboration
//   File Author: Emily Boudreaux
//   Last Modified: March 26, 2025
//
//   4DSSE is free software; you can use it and/or modify
//   it under the terms and restrictions the GNU General Library Public
//   License version 3 (GPLv3) as published by the Free Software Foundation.
//
//   4DSSE is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
//   See the GNU Library General Public License for more details.
//
//   You should have received a copy of the GNU Library General Public License
//   along with this software; if not, write to the Free Software
//   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
//
// *********************************************************************** */
#pragma once

#include <string>
#include <iostream>
#include <sstream>
#include <vector>
#include <map>
#include <algorithm>
#include <stdexcept>

// Required for YAML parsing
#include "yaml-cpp/yaml.h"

// -- Forward Def of Resource manager to let it act as a friend of Config --
// Note this is for SERiF development
namespace serif::resource { class ResourceManager; }

class configTestPrivateAccessor; // Forward declaration for test utility

namespace fourdst::config {

   /**
 * @class Config
 * @brief Singleton class to manage configuration settings loaded from a YAML file.
 */
   class Config {
   private:
      /**
    * @brief Private constructor to prevent instantiation.
    */
      Config();

      /**
    * @brief Destructor.
    */
      ~Config();

      YAML::Node yamlRoot; ///< Root node of the YAML configuration.
      std::string configFilePath; ///< Path to the configuration file.
      bool debug = false; ///< Flag to enable debug output.
      bool loaded = false; ///< Flag to indicate if the configuration has been loaded.

      std::map<std::string, YAML::Node> configMap; ///< Cache for the location of configuration settings.
      std::vector<std::string> unknownKeys; ///< Cache for the existence of configuration settings.

      /**
    * @brief Get a value from the configuration cache.
    * @tparam T Type of the value to retrieve.
    * @param key Key of the configuration value.
    * @param defaultValue Default value to return if the key does not exist.
    * @return Configuration value of type T.
    */
      template <typename T>
      T getFromCache(const std::string &key, T defaultValue) {
         if (configMap.find(key) != configMap.end()) {
            try {
               return configMap[key].as<T>();
            } catch (const YAML::Exception& e) {
               return defaultValue;
            }
         }
         return defaultValue;
      }


      /**
    * @brief Check if a key exists in the configuration cache.
    * @param key Key to check.
    * @return True if the key exists in the cache, false otherwise.
    */
      bool isKeyInCache(const std::string &key);

      /**
    * @brief Add a key-value pair to the configuration cache.
    * @param key Key of the configuration value.
    * @param node YAML node containing the configuration value.
    */
      void addToCache(const std::string &key, const YAML::Node &node);

      /**
    * @brief Register a key as not found in the configuration.
    * @param key Key that was not found.
    */
      void registerUnknownKey(const std::string &key);

      bool m_loaded = false;

      // Only friends can access get without a default value
      template <typename T>
      T get(const std::string &key) {
         if (!m_loaded) {
            throw std::runtime_error("Error! Config file not loaded");
         }
         if (has(key)) {
            return getFromCache<T>(key, T());
         } else {
            throw std::runtime_error("Error! Key not found in config file");
         }
      }

   public:
      /**
    * @brief Get the singleton instance of the Config class.
    * @return Reference to the Config instance.
    */
      static Config& getInstance();

      Config (const Config&) = delete;
      Config& operator= (const Config&) = delete;
      Config (Config&&) = delete;
      Config& operator= (Config&&) = delete;

      void setDebug(bool debug) { this->debug = debug; }

      /**
    * @brief Load configuration from a YAML file.
    * @param configFilePath Path to the YAML configuration file.
    * @return True if the configuration was loaded successfully, false otherwise.
    */
      bool loadConfig(const std::string& configFilePath);

      /**
    * @brief Get the input table from the configuration.
    * @return Input table as a string.
    */
      std::string getInputTable() const;

      /**
    * @brief Get a configuration value by key.
    * @tparam T Type of the value to retrieve.
    * @param key Key of the configuration value.
    * @param defaultValue Default value to return if the key does not exist.
    * @return Configuration value of type T.
    *
    * @example
    * @code
    * Config& config = Config::getInstance();
    * config.loadConfig("example.yaml");
    * int maxIter = config.get<int>("opac:lowTemp:numeric:maxIter", 10);
    */
      template <typename T>
      T get(const std::string &key, T defaultValue) {
         if (!m_loaded) {
            // ONLY THROW ERROR IF HARSH OR WARN CONFIGURATION
#if defined(CONFIG_HARSH)
         throw std::runtime_error("Error! Config file not loaded. To disable this error, recompile with CONFIG_HARSH=0");
#elif defined(CONFIG_WARN)
         std::cerr << "Warning! Config file not loaded. This instance of 4DSSE was compiled with CONFIG_WARN so the code will continue using only default values" << std::endl;
#endif
         }
         // --- Check if the key has already been checked for existence
         if (std::find(unknownKeys.begin(), unknownKeys.end(), key) != unknownKeys.end()) {
            return defaultValue; // If the key has already been added to the unknown cache do not traverse the YAML tree or hit the cache
         }

         // --- Check if the key is already in the cache (avoid traversing YAML nodes)
         if (isKeyInCache(key)) {
            return getFromCache<T>(key, defaultValue);
         }
         // --- If the key is not in the cache, check the YAML file
         else {
            YAML::Node node = YAML::Clone(yamlRoot);
            std::istringstream keyStream(key);
            std::string subKey;
            while (std::getline(keyStream, subKey, ':')) {
               if (!node[subKey]) {
                  // Key does not exist
                  registerUnknownKey(key);
                  return defaultValue;
               }
               node = node[subKey]; // go deeper
            }

            try {
               // Key exists and is of the requested type
               addToCache(key, node);
               return node.as<T>();
            } catch (const YAML::Exception& e) {
               // Key is not of the requested type
               registerUnknownKey(key);
               return defaultValue; // return default value if the key does not exist
            }
         }
      }

      /**
   * @brief Check if the key exists in the given config file
   * @param key Key to check;
   * @return boolean true or false
   */
      bool has(const std::string &key);

      /**
   * @brief Get all keys defined in the configuration file.
   * @return Vector of all keys in the configuration file.
   */
      std::vector<std::string> keys() const;

      /**
    * @brief Print the configuration file path and the YAML root node.
    * @param os Output stream.
    * @param config Config object to print.
    * @return Output stream.
    */
      friend std::ostream& operator<<(std::ostream& os, const Config& config) {
         if (!config.m_loaded) {
            os << "Config file not loaded" << std::endl;
            return os;
         }
         if (!config.debug) {
            os << "Config file: " << config.configFilePath << std::endl;
         } else{
            // Print entire YAML file from root
            os << "Config file: " << config.configFilePath << std::endl;
            os << config.yamlRoot << std::endl;
         }
         return os;
      }

      // Setup gTest class as a friend
      friend class ::configTestPrivateAccessor; // Friend declaration for global test accessor
      // -- Resource Manager is a friend of config so it can create a seperate instance
      friend class serif::resource::ResourceManager; // Adjusted friend declaration
   };

}
