require 'rails_helper'

RSpec.describe SkillsService, type: :service do
  describe '.list' do
    let!(:skill1) { create(:skill, name: 'skill_a', created_at: 1.day.ago) }
    let!(:skill2) { create(:skill, name: 'skill_b', created_at: 2.days.ago) }

    it 'returns all skills ordered by created_at desc' do
      result = described_class.list({})
      expect(result.to_a).to eq([ skill1, skill2 ])
    end

    it 'filters by name' do
      result = described_class.list({ name: 'skill_a' })
      expect(result).to contain_exactly(skill1)
    end
  end

  describe '.get' do
    let!(:skill) { create(:skill) }

    it 'returns the skill by id' do
      expect(described_class.get(skill.id)).to eq(skill)
    end

    it 'raises ActiveRecord::RecordNotFound for missing id' do
      expect { described_class.get(999_999) }.to raise_error(ActiveRecord::RecordNotFound)
    end
  end

  describe '.create' do
    let(:valid_params) do
      {
        name: 'new_skill',
        description: 'A skill',
        prompt: 'You are {{task}}',
        input_schema: { type: 'object' },
        output_schema: { type: 'object' },
        version: 1,
        metadata: { key: 'value' }
      }
    end

    it 'creates a skill with valid params' do
      skill = described_class.create(valid_params)
      expect(skill.name).to eq('new_skill')
      expect(skill.version).to eq(1)
    end

    it 'raises error with invalid params' do
      expect { described_class.create({ name: '' }) }.to raise_error(ActiveRecord::RecordInvalid)
    end
  end

  describe '.execute' do
    let!(:skill) { create(:skill) }

    it 'creates and completes an execution' do
      execution = described_class.execute(skill.id, { task: 'test' })
      expect(execution.status).to eq('completed')
      expect(execution.output).to be_present
      expect(execution.executed_at).to be_present
    end

    it 'raises error for non-existent skill' do
      expect { described_class.execute(999_999, {}) }.to raise_error(ActiveRecord::RecordNotFound)
    end
  end
end
