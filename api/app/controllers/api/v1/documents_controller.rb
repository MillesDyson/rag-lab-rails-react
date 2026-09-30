module Api
  module V1
    class DocumentsController < ApplicationController
      before_action :authorize_internal!, only: :ingested
      before_action :set_document, only: %i[destroy text ingested]

      def index
        render json: Document.recent.map { |document| DocumentSerializer.call(document) }
      end

      def create
        upload = params[:file]
        return render json: { error: "nenhum arquivo enviado" }, status: :unprocessable_entity if upload.blank?

        document = Document.from_upload(upload)

        if document.save
          IngestDocumentJob.perform_later(document.id)
          render json: DocumentSerializer.call(document), status: :created
        else
          render json: { error: document.errors.full_messages.to_sentence }, status: :unprocessable_entity
        end
      end

      # GET /api/v1/documents/:id/text
      def text
        render json: { text: @document.extracted_text }
      end

      def destroy
        IngestClient.new.delete_vectors(@document.id)
        @document.destroy!
        head :no_content
      end

      # POST /api/v1/documents/:id/ingested
      def ingested
        @document.update!(ingestion_params)
        head :ok
      end

      private

      def set_document
        @document = Document.find(params[:id])
      end

      def ingestion_params
        params.permit(
          :status, :kind, :chunks_count, :characters_count,
          :extracted_text, :extracted_preview, :error
        )
      end

      def authorize_internal!
        expected = ENV.fetch("INTERNAL_TOKEN", "dev-token-trocar-depois")
        return if ActiveSupport::SecurityUtils.secure_compare(
          request.headers["X-Internal-Token"].to_s, expected
        )

        head :unauthorized
      end
    end
  end
end
