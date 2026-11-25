using System.Text.Json.Serialization;

namespace TitanicSafetyApp.Models;

public sealed class PredictionRequest
{
    [JsonPropertyName("pclass")]
    public int Pclass { get; init; }

    [JsonPropertyName("sex")]
    public string Sex { get; init; } = "male";

    [JsonPropertyName("age")]
    public double Age { get; init; }

    [JsonPropertyName("sibsp")]
    public int SibSp { get; init; }

    [JsonPropertyName("parch")]
    public int Parch { get; init; }

    [JsonPropertyName("fare")]
    public double Fare { get; init; }

    [JsonPropertyName("embarked")]
    public string Embarked { get; init; } = "S";

    [JsonPropertyName("title")]
    public string Title { get; init; } = "Mr";

    [JsonPropertyName("has_cabin")]
    public int HasCabin { get; init; }
}

public sealed class PredictionResponse
{
    [JsonPropertyName("survived")]
    public int Survived { get; set; }

    [JsonPropertyName("label")]
    public string Label { get; set; } = "";

    [JsonPropertyName("probability_survived")]
    public double ProbabilitySurvived { get; set; }

    [JsonPropertyName("probability_not_survived")]
    public double ProbabilityNotSurvived { get; set; }

    [JsonPropertyName("risk_level")]
    public string RiskLevel { get; set; } = "";
}

public sealed class HealthResponse
{
    [JsonPropertyName("status")]
    public string Status { get; set; } = "";

    [JsonPropertyName("model_loaded")]
    public bool ModelLoaded { get; set; }

    [JsonPropertyName("model_type")]
    public string? ModelType { get; set; }

    [JsonPropertyName("feature_count")]
    public int? FeatureCount { get; set; }

    [JsonPropertyName("message")]
    public string Message { get; set; } = "";

    [JsonPropertyName("api_version")]
    public string ApiVersion { get; set; } = "";
}
