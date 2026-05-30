module Api
  module V1
    class SkillsController < BaseController
      def index
        skills = SkillsService.list(index_params)
        render json: skills.as_json(only: [ :id, :name, :description, :version, :created_at, :updated_at ])
      end

      def show
        skill = SkillsService.get(params[:id])
        render json: skill.as_json(only: [ :id, :name, :description, :prompt, :input_schema, :output_schema, :version, :metadata, :created_at, :updated_at ])
      end

      def create
        skill = SkillsService.create(create_params)
        render json: skill.as_json(only: [ :id, :name, :description, :prompt, :input_schema, :output_schema, :version, :metadata, :created_at, :updated_at ]),
               status: :created
      end

      def execute
        execution = SkillsService.execute(params[:id], execute_params[:input] || {})
        render json: execution.as_json(
          only: [ :id, :skill_id, :input, :output, :status, :error_message, :executed_at, :verified_at, :created_at, :updated_at ],
          include: { skill: { only: [ :id, :name, :version ] } }
        )
      end

      private

      def index_params
        params.permit(:name)
      end

      def create_params
        params.require(:skill).permit(:name, :description, :prompt, :version, input_schema: {}, output_schema: {}, metadata: {})
      end

      def execute_params
        params.permit(input: {})
      end
    end
  end
end
