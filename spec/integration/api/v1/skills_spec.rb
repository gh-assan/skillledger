require 'swagger_helper'

RSpec.describe 'API V1 Skills', type: :request do
  path '/api/v1/skills' do
    get('list skills') do
      tags 'Skills'
      produces 'application/json'
      parameter name: :name, in: :query, type: :string, required: false,
                description: 'Filter by skill name'

      response(200, 'successful') do
        let!(:skill) { create(:skill) }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data).to be_an(Array)
        end
      end
    end

    post('create skill') do
      tags 'Skills'
      consumes 'application/json'
      produces 'application/json'
      parameter name: :body, in: :body, schema: { '$ref' => '#/components/schemas/SkillInput' }

      response(201, 'created') do
        let(:body) do
          {
            skill: {
              name: 'new_skill',
              description: 'A new skill',
              prompt: 'You are helpful',
              input_schema: { type: 'object' },
              output_schema: { type: 'object' },
              version: 1,
              metadata: {}
            }
          }
        end

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['name']).to eq('new_skill')
        end
      end

      response(422, 'unprocessable entity') do
        let(:body) { { skill: { name: '' } } }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['error']).to be_present
        end
      end
    end
  end

  path '/api/v1/skills/{id}' do
    get('show skill') do
      tags 'Skills'
      produces 'application/json'
      parameter name: :id, in: :path, type: :integer, required: true

      response(200, 'successful') do
        let(:skill) { create(:skill) }
        let(:id) { skill.id }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['id']).to eq(skill.id)
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

  path '/api/v1/skills/{id}/execute' do
    post('execute skill') do
      tags 'Skills'
      consumes 'application/json'
      produces 'application/json'
      parameter name: :id, in: :path, type: :integer, required: true
      parameter name: :body, in: :body, schema: { '$ref' => '#/components/schemas/ExecuteInput' }

      response(200, 'successful') do
        let(:skill) { create(:skill) }
        let(:id) { skill.id }
        let(:body) { { input: { task: 'test' } } }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['skill_id']).to eq(skill.id)
          expect(data['status']).to eq('completed')
        end
      end

      response(404, 'not found') do
        let(:id) { 999_999 }
        let(:body) { { input: {} } }

        run_test! do |response|
          data = JSON.parse(response.body)
          expect(data['error']).to be_present
        end
      end
    end
  end
end
