require "net/http"
require "json"

class IngestClient
  class Error < StandardError; end

  def initialize(base_url: ENV.fetch("INGEST_SERVICE_URL", "http://localhost:8000"))
    @base_url = base_url
  end

  def ingest(document, file_url:)
    post("/ingest", {
      document_id: document.id,
      file_url: file_url,
      content_type: document.content_type,
      filename: document.filename
    })
  end

  def query(question, k:, kinds:)
    post("/query", { question: question, k: k, kinds: kinds.presence })
  end

  def delete_vectors(document_id)
    request(Net::HTTP::Delete.new(uri_for("/documents/#{document_id}")))
  rescue Error => e
    Rails.logger.warn("[IngestClient] falha ao apagar vetores do documento #{document_id}: #{e.message}")
  end

  private

  def post(path, payload)
    request = Net::HTTP::Post.new(uri_for(path))
    request["Content-Type"] = "application/json"
    request.body = payload.to_json
    request(request)
  end

  def request(request)
    uri = request.uri
    request["X-Internal-Token"] = ENV.fetch("INTERNAL_TOKEN", "dev-token-trocar-depois")

    response = Net::HTTP.start(uri.hostname, uri.port, read_timeout: 30) do |http|
      http.request(request)
    end

    raise Error, "#{response.code} #{response.body}" unless response.is_a?(Net::HTTPSuccess)

    response.body.presence && JSON.parse(response.body)
  rescue SystemCallError, Net::OpenTimeout, Net::ReadTimeout => e
    raise Error, "servico de ingestao indisponivel (#{e.class})"
  end

  def uri_for(path)
    URI.join(@base_url, path)
  end
end
