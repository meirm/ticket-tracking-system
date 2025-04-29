# This ensures that Django uses the custom AccountsConfig
# which loads signals for automatic UserProfile creation

default_app_config = 'accounts.apps.AccountsConfig'
