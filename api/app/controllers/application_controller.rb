class ApplicationController < ActionController::API
  rescue_from ActiveRecord::RecordNotFound do
    render json: { error: "documento nao encontrado" }, status: :not_found
  end
end
