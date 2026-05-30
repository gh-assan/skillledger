FactoryBot.define do
  factory :execution do
    skill
    input { { task: 'test' } }
    status { 'pending' }
  end
end
