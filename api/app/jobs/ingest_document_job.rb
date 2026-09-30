class IngestDocumentJob < ApplicationJob
  queue_as :default

  def perform(document_id)
    document = Document.find(document_id)
    document.processing!

    IngestClient.new.ingest(document, file_url: file_url_for(document))
  rescue IngestClient::Error => e
    document&.failed!(e.message)
  end

  private

  # URL assinada que o container de ingestao usa para baixar o arquivo.
  # O host precisa ser o nome do servico no compose, nao localhost.
  def file_url_for(document)
    Rails.application.routes.url_helpers.rails_blob_url(
      document.file,
      host: ENV.fetch("RAILS_HOST", "localhost:3000"),
      protocol: "http"
    )
  end
end
