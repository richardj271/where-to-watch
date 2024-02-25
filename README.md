# where-to-watch
Look up films in Trakt watchlist on JustWatch to find which streaming service they're available on and store using Baserow.

## Baserow

* You'll need a Baserow account
* Create a database, you can call it anything e.g. "Where to watch".
* Create a database token for that database
    * In Settings > Database tokens click "Create token +".
    * You can call it anything e.g. "Where to watch", select the workspace you created the database in.
    * Click 'show databases' for the token you just created, remove any that aren't the database you just created.
    * Copy the token by clicking on the '...'
* You can optionally delete the default table, called "Table"
* Create a table called 'Films', select "Start with a new table", leave the default content as is
* You'll need [the ID of this table](https://baserow.io/user-docs/database-and-table-id)


## Secrets

* Secrets are read from environment variables.
* This works well with GitHub Codespaces, just use [Codespace secrets](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-your-account-specific-secrets-for-github-codespaces).
* The three environment variables you need to set are:
    * `BASEROW_TOKEN_WHERE_TO_WATCH`
    * `BASEROW_FILMS_TABLE_ID`
    * `TRAKT_CLIENT_ID_WHERE_TO_WATCH`
    * `TRAKT_USER_ID`

## Trakt

* You'll need a Trakt account
* Create an app in Settings > You API Apps
<!-- TODO: Need instructions for setting up Trakt api app -->
<!-- TODO: Need instructions for getting user ID esp. the dots being dashes etc. -->

Consider using python-dotenv
Create table from scratch: https://baserow.io/docs/apis%2Frest-api, https://api.baserow.io/api/redoc/#tag/Database-tables/operation/create_database_table