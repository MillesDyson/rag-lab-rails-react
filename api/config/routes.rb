Rails.application.routes.draw do
  namespace :api do
    namespace :v1 do
      resource :search, only: :create, controller: "searches"

      resources :documents, only: %i[index create destroy] do
        member do
          get :text

          post :ingested
        end
      end
    end
  end
end
