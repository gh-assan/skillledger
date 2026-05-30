require 'rails_helper'

RSpec.describe Skill, type: :model do
  subject { build(:skill) }

  it { is_expected.to validate_presence_of(:name) }
  it { is_expected.to validate_uniqueness_of(:name) }
  it { is_expected.to validate_numericality_of(:version).is_greater_than(0) }
  it { is_expected.to have_many(:executions).dependent(:destroy) }
end
