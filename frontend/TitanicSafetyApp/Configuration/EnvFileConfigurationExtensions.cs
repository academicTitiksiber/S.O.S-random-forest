namespace TitanicSafetyApp.Configuration;

public static class EnvFileConfigurationExtensions
{
    public static IConfigurationBuilder AddEnvFile(this IConfigurationBuilder builder, string contentRootPath)
    {
        var parentPath = Directory.GetParent(contentRootPath)?.FullName ?? contentRootPath;
        var candidates = new[]
        {
            Path.Combine(contentRootPath, ".env"),
            Path.Combine(parentPath, ".env")
        };

        var envPath = candidates.FirstOrDefault(File.Exists);
        if (envPath is null)
        {
            return builder;
        }

        var values = new Dictionary<string, string?>();
        foreach (var rawLine in File.ReadAllLines(envPath))
        {
            var line = rawLine.Trim();
            if (line.Length == 0 || line.StartsWith('#'))
            {
                continue;
            }

            var separator = line.IndexOf('=');
            if (separator <= 0)
            {
                continue;
            }

            var key = line[..separator].Trim();
            var value = line[(separator + 1)..].Trim().Trim('"', '\'');
            values[key] = value;
        }

        return builder.AddInMemoryCollection(values);
    }
}
