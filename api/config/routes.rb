Rails.application.routes.draw do
  namespace :api do
    namespace :v1 do
      resources :documents, only: %i[index create destroy] do
        member do
          # chamado pelo servico de ingestao quando termina (ou falha)
          post :ingested
        end
      end
    end
  end
end
