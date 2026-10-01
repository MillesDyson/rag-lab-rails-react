module Api
  module V1
    class SearchesController < ApplicationController
      MAX_RESULTS = 10

      def create
        question = params[:question].to_s.strip
        return render json: { error: "informe uma pergunta" }, status: :unprocessable_entity if question.blank?

        result = IngestClient.new.query(question, k: results_count, kinds: params[:kinds])
        render json: { answer: result["answer"], sources: decorate(result["sources"]) }
      rescue IngestClient::Error => e
        render json: { error: e.message }, status: :bad_gateway
      end

      private

      def results_count
        params.fetch(:k, 5).to_i.clamp(1, MAX_RESULTS)
      end

      def decorate(sources)
        documents = Document.where(id: sources.map { |s| s["document_id"] }.uniq).index_by(&:id)

        sources.map do |source|
          document = documents[source["document_id"]]
          {
            documentId: source["document_id"],
            filename: document&.filename || source["filename"],
            kind: source["kind"],
            chunkIndex: source["chunk_index"],
            score: source["score"],
            excerpt: source["excerpt"],
            missing: document.nil?
          }
        end
      end
    end
  end
end
