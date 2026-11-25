namespace TitanicSafetyApp.Services;

public sealed class TitanicApiException : Exception
{
    public TitanicApiException(string message, string code, string? rawBody = null) : base(message)
    {
        Code = code;
        RawBody = rawBody;
    }

    public string Code { get; }

    public string? RawBody { get; }
}
