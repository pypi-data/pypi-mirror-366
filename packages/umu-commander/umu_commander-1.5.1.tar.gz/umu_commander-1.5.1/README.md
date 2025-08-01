## umu-commander
### umu-commander is an interactive CLI tool to help you manage Proton versions used by umu, as well as create enhanced launch configs.

Proton versions can be tracked and untracked, with the intention of being safely removable once no game depends on a specific one.\
What directories each Proton version is being used by is tracked within `tracking.json` inside your umu Proton directory by default.

Vanilla umu configuration files currently do not support setting environmental variables, this tool adds such functionality by adding an extra TOML table in the umu config itself. An example config is available under the name `example_config.toml`.

umu-commander will look for your installed Proton versions using a predetermined list of directories, if you notice some versions missing, the listed can be edited within the `configuration.py` file in the src directory.

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