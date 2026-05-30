require 'swagger_helper'

RSpec.describe 'API V1 Health', type: :request do
  path '/api/v1/health' do
    get('show health') do
      tags 'Health'
      produces 'application/json'

      response(200, 'successful') do
        schema '$ref' => '#/components/schemas/Health'

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['status']).to eq('ok')
          expect(data['database']).to be true
        end
      end
    end
  end
end
