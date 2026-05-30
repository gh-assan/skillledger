require 'rails_helper'

RSpec.describe Execution, type: :model do
  subject { build(:execution) }

  it { is_expected.to belong_to(:skill) }
  it { is_expected.to validate_presence_of(:status) }
  it { is_expected.to validate_inclusion_of(:status).in_array(%w[pending running completed failed verified]) }
end
