FactoryBot.define do
  factory :skill do
    name { "skill_#{SecureRandom.hex(4)}" }
    description { 'A test skill' }
    prompt { 'You are an AI assistant that helps with {{task}}' }
    input_schema { { type: 'object', properties: { task: { type: 'string' } } } }
    output_schema { { type: 'object', properties: { result: { type: 'string' } } } }
    version { 1 }
    metadata { { author: 'test' } }
  end
end
