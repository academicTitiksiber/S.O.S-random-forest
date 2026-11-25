using TitanicSafetyApp.Models;

namespace TitanicSafetyApp.Services;

public interface ITitanicApiClient
{
    Task<PredictionResponse> PredictAsync(PredictionRequest request, CancellationToken cancellationToken = default);

    Task<HealthResponse> GetHealthAsync(CancellationToken cancellationToken = default);
}
