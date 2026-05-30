source "https://rubygems.org"

gem "rails", "~> 8.1.3"
gem "sqlite3", ">= 2.1"
gem "puma", ">= 5.0"
gem "bootsnap", require: false
gem "tzinfo-data", platforms: %i[ windows jruby ]

# CORS
gem "rack-cors"

# Environment variables
gem "dotenv-rails"

# PostgreSQL for production
gem "pg", group: :production

group :development, :test do
  gem "debug", platforms: %i[ mri windows ], require: "debug/prelude"
  gem "bundler-audit", require: false
  gem "brakeman", require: false
  gem "rubocop-rails-omakase", require: false

  # Testing
  gem "rspec-rails", "~> 8.0"
  gem "factory_bot_rails"
  gem "simplecov", require: false
  gem "shoulda-matchers", "~> 6.0"
end

group :development, :test do
  # OpenAPI / Swagger docs
  gem "rswag-specs"
end

gem "rswag-api"
gem "rswag-ui"
