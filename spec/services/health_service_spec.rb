require 'rails_helper'

RSpec.describe HealthService, type: :service do
  describe '.check' do
    it 'returns a health status hash' do
      result = described_class.check
      expect(result[:status]).to eq('ok')
      expect(result[:database]).to be true
      expect(result[:timestamp]).to be_present
      expect(result[:version]).to eq('1.0.0')
    end
  end
end
