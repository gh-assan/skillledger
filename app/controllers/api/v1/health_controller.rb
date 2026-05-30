module Api
  module V1
    class HealthController < BaseController
      def show
        render json: HealthService.check
      end
    end
  end
end
