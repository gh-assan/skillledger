require 'swagger_helper'

RSpec.describe 'API V1 Accounts', type: :request do
  path '/api/v1/accounts' do
    post('create account') do
      tags 'Accounts'
      consumes 'application/json'
      produces 'application/json'
      parameter name: :body, in: :body, schema: { '$ref' => '#/components/schemas/AccountInput' }

      response(201, 'created') do
        let(:body) do
          {
            account: {
              name: 'test_account',
              balance: 100.0
            }
          }
        end

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['name']).to eq('test_account')
          expect(data['balance'].to_f).to eq(100.0)
        end
      end

      response(422, 'unprocessable entity') do
        let(:body) { { account: { name: '' } } }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['error']).to be_present
        end
      end
    end
  end

  path '/api/v1/accounts/{id}/balance' do
    get('get account balance') do
      tags 'Accounts'
      produces 'application/json'
      parameter name: :id, in: :path, type: :integer, required: true

      response(200, 'successful') do
        let(:account) { create(:account) }
        let(:id) { account.id }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['id']).to eq(account.id)
          expect(data['balance'].to_f).to eq(account.balance.to_f)
        end
      end

      response(404, 'not found') do
        let(:id) { 999_999 }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['error']).to be_present
        end
      end
    end
  end
end
