## umu-commander
### umu-commander is an interactive CLI tool to help you manage Proton versions used by umu, as well as create enhanced launch configs.

Proton versions can be tracked and untracked, with the intention of being safely removable once no game depends on a specific one.\
What directories each Proton version is being used by is tracked within `tracking.json` inside your umu Proton directory by default.

Vanilla umu configuration files currently do not support setting environmental variables, this tool adds such functionality by adding an extra TOML table in the umu config itself. An example config is available under the name `example_config.toml`.

### Config
The configuration file lives at `~/.config/umu-commander.toml`. Within it, you can edit the following:
* PROTON_PATHS: List of directories umu-commander will search for Proton versions.
* UMU_PROTON_PATH: Directory where umu itself downloads its umu Proton versions.
* DB_NAME: Tracking DB filename.
* DB_DIR: Directory where the Tracking DB is stored.
* UMU_CONFIG_NAME: Name of the umu config created using umu-commander run.
* DEFAULT_PREFIX_DIR: Directory where WINE prefixes are scanned.
* [DLL_OVERRIDES_OPTIONS]: Category to list possible DLL overrides in "Label" = "Override string" format.

### Verbs
umu-commander needs one of the following verbs specified after the executable name:
* track: Adds the current directory to a specified Proton version's list of users.
  * If the directory is already in another list, it will be removed from it.
  * The create verb will automatically track the current directory.
  * This will not update any existing configs.
* untrack:  Removes the current directory from all tracking lists.
* users: Lists each Proton version's users.
* delete: Interactively deletes any Proton version in the tracking database with no users.
  * This will actually remove the Proton directories, use at your own risk.
  * If a Proton version has not been tracked before, it will not be removed, neither will the latest umu Proton.
  * umu-commander will not delete anything without invoking this verb and receiving confirmation.
* create: Creates a custom configuration file in the current directory.
* run: Uses the config in the current directory to run the program.
  * This is NOT equivalent to `umu-run --config <config_name>`, as vanilla umu configs do not support setting environment variables as of 07/2025.
  
### Installation/Usage
Add umu-run to your PATH and then install with pipx by running `pipx install umu-commander`. After that you can invoke umu-commander by running `umu-commander <verb>`. 

### Return codes
| Number | Name              | Description                                                     |
|:-------|:------------------|:----------------------------------------------------------------|
| 0      | SUCCESS           | Program executed as intended.                                   |
| 1      | READING_ERROR     | Failed to parse a file and could not recover.                   |
| 2      | INVALID_SELECTION | User selected an invalid verb or there are no valid selections. |
