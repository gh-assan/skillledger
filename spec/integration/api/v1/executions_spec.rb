require 'swagger_helper'

RSpec.describe 'API V1 Executions', type: :request do
  path '/api/v1/executions' do
    get('list executions') do
      tags 'Executions'
      produces 'application/json'
      parameter name: :skill_id, in: :query, type: :integer, required: false
      parameter name: :status, in: :query, type: :string, required: false

      response(200, 'successful') do
        let!(:execution) { create(:execution) }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data).to be_an(Array)
        end
      end
    end
  end

  path '/api/v1/executions/{id}' do
    get('show execution') do
      tags 'Executions'
      produces 'application/json'
      parameter name: :id, in: :path, type: :integer, required: true

      response(200, 'successful') do
        let(:execution) { create(:execution) }
        let(:id) { execution.id }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['id']).to eq(execution.id)
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

  path '/api/v1/executions/{id}/verify' do
    post('verify execution') do
      tags 'Executions'
      produces 'application/json'
      parameter name: :id, in: :path, type: :integer, required: true

      response(200, 'successful') do
        let(:execution) { create(:execution, status: 'completed') }
        let(:id) { execution.id }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['status']).to eq('verified')
        end
      end

      response(422, 'unprocessable entity') do
        let(:execution) { create(:execution, status: 'pending') }
        let(:id) { execution.id }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['error']).to be_present
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
