require 'rails_helper'

RSpec.describe AccountsService, type: :service do
  describe '.create' do
    it 'creates an account with valid params' do
      account = described_class.create({ name: 'my_account', balance: 50.0 })
      expect(account.name).to eq('my_account')
      expect(account.balance).to eq(50.0)
    end

    it 'creates an account with default balance' do
      account = described_class.create({ name: 'no_balance' })
      expect(account.balance).to eq(0.0)
    end

    it 'raises error with invalid params' do
      expect { described_class.create({ name: '' }) }.to raise_error(ActiveRecord::RecordInvalid)
    end
  end

  describe '.get_balance' do
    let!(:account) { create(:account) }

    it 'returns the account' do
      result = described_class.get_balance(account.id)
      expect(result).to eq(account)
    end

    it 'raises error for non-existent account' do
      expect { described_class.get_balance(999_999) }.to raise_error(ActiveRecord::RecordNotFound)
    end
  end
end
