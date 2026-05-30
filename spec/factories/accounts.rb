FactoryBot.define do
  factory :account do
    name { "account_#{SecureRandom.hex(4)}" }
    balance { 100.0 }
  end
end
