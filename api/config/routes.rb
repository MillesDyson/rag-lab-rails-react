Rails.application.routes.draw do
  namespace :api do
    namespace :v1 do
      resources :documents, only: %i[index create destroy] do
        member do
          # o texto extraido pode ser longo (transcricao de video inteira),
          # entao fica fora da listagem e e buscado sob demanda
          get :text

          # chamado pelo servico de ingestao quando termina (ou falha)
          post :ingested
        end
      end
    end
  end
end
