module Api
  module V1
    class ExecutionsController < BaseController
      def index
        executions = ExecutionsService.list(index_params)
        render json: executions.as_json(
          only: [ :id, :skill_id, :input, :output, :status, :error_message, :executed_at, :verified_at, :created_at, :updated_at ],
          include: { skill: { only: [ :id, :name, :version ] } }
        )
      end

      def show
        execution = ExecutionsService.get(params[:id])
        render json: execution.as_json(
          only: [ :id, :skill_id, :input, :output, :status, :error_message, :executed_at, :verified_at, :created_at, :updated_at ],
          include: { skill: { only: [ :id, :name, :version ] } }
        )
      end

      def verify
        execution = ExecutionsService.verify(params[:id])
        render json: execution.as_json(
          only: [ :id, :skill_id, :input, :output, :status, :error_message, :executed_at, :verified_at, :created_at, :updated_at ],
          include: { skill: { only: [ :id, :name, :version ] } }
        )
      end

      private

      def index_params
        params.permit(:skill_id, :status)
      end
    end
  end
end
