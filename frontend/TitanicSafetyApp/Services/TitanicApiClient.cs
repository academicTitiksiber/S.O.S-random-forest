using System.Net.Http.Json;
using System.Text.Json;
using TitanicSafetyApp.Models;

namespace TitanicSafetyApp.Services;

public sealed class TitanicApiClient : ITitanicApiClient
{
    private const string HttpClientName = "TitanicApi";

    private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web);

    private readonly IHttpClientFactory _httpClientFactory;

    public TitanicApiClient(IHttpClientFactory httpClientFactory)
    {
        _httpClientFactory = httpClientFactory;
    }

    public async Task<PredictionResponse> PredictAsync(
        PredictionRequest request,
        CancellationToken cancellationToken = default)
    {
        var client = _httpClientFactory.CreateClient(HttpClientName);

        try
        {
            using var response = await client.PostAsJsonAsync(
                "/api/predict", request, JsonOptions, cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                throw await BuildApiExceptionAsync(response, cancellationToken);
            }

            var result = await response.Content.ReadFromJsonAsync<PredictionResponse>(
                JsonOptions, cancellationToken);

            return result ?? throw new TitanicApiException(
                "Backend mengembalikan respons prediksi kosong.", "EMPTY_RESPONSE");
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            throw new TitanicApiException(
                "Permintaan prediksi timeout. Periksa koneksi ke backend lalu coba lagi.", "TIMEOUT");
        }
        catch (HttpRequestException ex)
        {
            throw new TitanicApiException(
                "Tidak dapat terhubung ke backend API. Pastikan server FastAPI berjalan.",
                "CONNECTION_ERROR",
                ex.Message);
        }
    }

    public async Task<HealthResponse> GetHealthAsync(CancellationToken cancellationToken = default)
    {
        var client = _httpClientFactory.CreateClient(HttpClientName);

        try
        {
            using var response = await client.GetAsync("/api/health", cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                throw await BuildApiExceptionAsync(response, cancellationToken);
            }

            var result = await response.Content.ReadFromJsonAsync<HealthResponse>(
                JsonOptions, cancellationToken);

            return result ?? throw new TitanicApiException(
                "Backend mengembalikan respons health check kosong.", "EMPTY_RESPONSE");
        }
        catch (OperationCanceledException) when (!cancellationToken.IsCancellationRequested)
        {
            throw new TitanicApiException(
                "Health check timeout. Backend mungkin tidak merespons.", "TIMEOUT");
        }
        catch (HttpRequestException ex)
        {
            throw new TitanicApiException(
                "Tidak dapat terhubung ke backend API. Pastikan server FastAPI berjalan.",
                "CONNECTION_ERROR",
                ex.Message);
        }
    }

    private static async Task<TitanicApiException> BuildApiExceptionAsync(
        HttpResponseMessage response,
        CancellationToken cancellationToken)
    {
        var body = await response.Content.ReadAsStringAsync(cancellationToken);
        var message = $"Backend mengembalikan HTTP {(int)response.StatusCode}.";
        var code = "HTTP_ERROR";
        var details = new List<string>();

        try
        {
            using var document = JsonDocument.Parse(body);
            var root = document.RootElement;

            if (root.TryGetProperty("error", out var error))
            {
                if (error.TryGetProperty("code", out var errorCode) && errorCode.ValueKind == JsonValueKind.String)
                {
                    code = errorCode.GetString() ?? code;
                }

                if (error.TryGetProperty("message", out var errorMessage) && errorMessage.ValueKind == JsonValueKind.String)
                {
                    message = errorMessage.GetString() ?? message;
                }

                if (error.TryGetProperty("details", out var errorDetails) && errorDetails.ValueKind == JsonValueKind.Array)
                {
                    foreach (var item in errorDetails.EnumerateArray())
                    {
                        if (item.ValueKind != JsonValueKind.Object)
                        {
                            continue;
                        }

                        var field = item.TryGetProperty("field", out var fieldElement)
                            ? fieldElement.GetString()
                            : null;
                        var detailMessage = item.TryGetProperty("message", out var messageElement)
                            ? messageElement.GetString()
                            : null;
                        if (!string.IsNullOrWhiteSpace(detailMessage))
                        {
                            details.Add(string.IsNullOrWhiteSpace(field)
                                ? detailMessage
                                : $"{field}: {detailMessage}");
                        }
                    }
                }
            }
            else if (root.TryGetProperty("detail", out var detail))
            {
                message = detail.ValueKind == JsonValueKind.String
                    ? detail.GetString() ?? message
                    : detail.ToString();
            }
        }
        catch (JsonException)
        {
            if (!string.IsNullOrWhiteSpace(body))
            {
                details.Add(body.Length > 300 ? body[..300] : body);
            }
        }

        if (details.Count > 0)
        {
            message += " " + string.Join(" ", details);
        }

        return new TitanicApiException(message, code, body);
    }
}
