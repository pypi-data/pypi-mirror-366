# data-source-local-python-package

Should be similar to entity-type-local-python-package

To create local package and remote package layers (not to create GraphQL and REST-API layers)

#database scripts
Please place <table-name>.py in /db
No need for seperate file for _ml table

# Create the files to create the database schema, tables, view and populate Meta Data and Test Date

/db/<table-name>.py - CREATE SCHEMA ... CREATE TABLE ... CREATE VIEW ...<br>
/db/<table-name>_insert.py to create records

# Update the setup.py (i.e.name, version)

# Please create test directory inside the directory of the project i.e. /<project-name>/tests

# Update the serverless.yml in the root directory

provider:
stage: play1

Update the endpoints in serverless.yml
