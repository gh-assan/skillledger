require 'rails_helper'

RSpec.describe ExecutionsService, type: :service do
  let!(:skill) { create(:skill) }

  describe '.list' do
    let!(:execution1) { create(:execution, skill: skill, created_at: 1.day.ago) }
    let!(:execution2) { create(:execution, skill: skill, created_at: 2.days.ago, status: 'completed') }

    it 'returns all executions ordered by created_at desc' do
      result = described_class.list({})
      expect(result.to_a).to eq([ execution1, execution2 ])
    end

    it 'filters by status' do
      result = described_class.list({ status: 'completed' })
      expect(result).to contain_exactly(execution2)
    end

    it 'filters by skill_id' do
      other_skill = create(:skill)
      create(:execution, skill: other_skill)

      result = described_class.list({ skill_id: skill.id })
      expect(result).to contain_exactly(execution1, execution2)
    end
  end

  describe '.get' do
    let!(:execution) { create(:execution, skill: skill) }

    it 'returns the execution by id' do
      expect(described_class.get(execution.id)).to eq(execution)
    end

    it 'includes the associated skill' do
      result = described_class.get(execution.id)
      expect(result.association(:skill)).to be_loaded
    end
  end

  describe '.verify' do
    it 'verifies a completed execution' do
      execution = create(:execution, skill: skill, status: 'completed')
      result = described_class.verify(execution.id)
      expect(result.status).to eq('verified')
      expect(result.verified_at).to be_present
    end

    it 'raises error for already verified execution' do
      execution = create(:execution, skill: skill, status: 'verified')
      expect { described_class.verify(execution.id) }.to raise_error(StandardError, /already verified/)
    end

    it 'raises error for pending execution' do
      execution = create(:execution, skill: skill, status: 'pending')
      expect { described_class.verify(execution.id) }.to raise_error(StandardError, /Cannot verify/)
    end
  end
end
