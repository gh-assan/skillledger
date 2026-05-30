require 'rails_helper'

RSpec.configure do |config|
  config.openapi_root = Rails.root.join('swagger').to_s

  config.openapi_specs = {
    'v1/swagger.yaml' => {
      openapi: '3.0.3',
      info: {
        title: 'SkillLedger API',
        version: 'v1',
        description: 'Skill execution and verification API'
      },
      paths: {},
      servers: [
        {
          url: 'http://localhost:3000',
          description: 'Development server'
        }
      ],
      components: {
        schemas: {
          Skill: {
            type: :object,
            properties: {
              id: { type: :integer },
              name: { type: :string },
              description: { type: :string, nullable: true },
              prompt: { type: :string, nullable: true },
              input_schema: { type: :object },
              output_schema: { type: :object },
              version: { type: :integer },
              metadata: { type: :object },
              created_at: { type: :string, format: 'date-time' },
              updated_at: { type: :string, format: 'date-time' }
            },
            required: [ :id, :name, :version ]
          },
          Execution: {
            type: :object,
            properties: {
              id: { type: :integer },
              skill_id: { type: :integer },
              input: { type: :object },
              output: { type: :object, nullable: true },
              status: { type: :string, enum: [ 'pending', 'running', 'completed', 'failed', 'verified' ] },
              error_message: { type: :string, nullable: true },
              executed_at: { type: :string, format: 'date-time', nullable: true },
              verified_at: { type: :string, format: 'date-time', nullable: true },
              created_at: { type: :string, format: 'date-time' },
              updated_at: { type: :string, format: 'date-time' },
              skill: { '$ref' => '#/components/schemas/Skill' }
            },
            required: [ :id, :skill_id, :status ]
          },
          Account: {
            type: :object,
            properties: {
              id: { type: :integer },
              name: { type: :string },
              balance: { type: :number, format: :decimal },
              created_at: { type: :string, format: 'date-time' },
              updated_at: { type: :string, format: 'date-time' }
            },
            required: [ :id, :name, :balance ]
          },
          Health: {
            type: :object,
            properties: {
              status: { type: :string },
              timestamp: { type: :string, format: 'date-time' },
              database: { type: :boolean },
              version: { type: :string }
            }
          },
          SkillInput: {
            type: :object,
            properties: {
              skill: {
                type: :object,
                properties: {
                  name: { type: :string },
                  description: { type: :string },
                  prompt: { type: :string },
                  input_schema: { type: :object },
                  output_schema: { type: :object },
                  version: { type: :integer },
                  metadata: { type: :object }
                },
                required: [ :name ]
              }
            }
          },
          ExecuteInput: {
            type: :object,
            properties: {
              input: { type: :object }
            }
          },
          AccountInput: {
            type: :object,
            properties: {
              account: {
                type: :object,
                properties: {
                  name: { type: :string },
                  balance: { type: :number }
                },
                required: [ :name ]
              }
            }
          },
          Error: {
            type: :object,
            properties: {
              error: { type: :string }
            }
          }
        }
      }
    }
  }

  config.openapi_format = :yaml
end
