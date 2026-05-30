Rails.application.routes.draw do
  mount Rswag::Ui::Engine => "/api-docs"
  mount Rswag::Api::Engine => "/api-docs"

  namespace :api do
    namespace :v1 do
      resources :skills, only: [ :index, :show, :create ] do
        member do
          post :execute
        end
      end

      resources :executions, only: [ :index, :show ] do
        member do
          post :verify
        end
      end

      resources :accounts, only: [ :create ] do
        member do
          get :balance
        end
      end

      get "health", to: "health#show"
    end
  end
end
