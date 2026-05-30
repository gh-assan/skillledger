module Api
  module V1
    class AccountsController < BaseController
      def create
        account = AccountsService.create(create_params)
        render json: account.as_json(only: [ :id, :name, :balance, :created_at, :updated_at ]),
               status: :created
      end

      def balance
        account = AccountsService.get_balance(params[:id])
        render json: account.as_json(only: [ :id, :name, :balance ])
      end

      private

      def create_params
        params.require(:account).permit(:name, :balance)
      end
    end
  end
end
