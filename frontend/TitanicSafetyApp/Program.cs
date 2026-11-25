using Microsoft.AspNetCore.DataProtection;
using TitanicSafetyApp.Components;
using TitanicSafetyApp.Configuration;
using TitanicSafetyApp.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Configuration.AddEnvFile(builder.Environment.ContentRootPath);

var configuredBaseUrl = builder.Configuration["API_BASE_URL"] ?? "http://localhost:8000";
if (!Uri.TryCreate(configuredBaseUrl, UriKind.Absolute, out var apiBaseUri))
{
    throw new InvalidOperationException(
        $"API_BASE_URL tidak valid: '{configuredBaseUrl}'. Gunakan format URL absolut seperti http://localhost:8000");
}

var keysPath = Path.GetFullPath(
    builder.Configuration["DATA_PROTECTION_KEYS_PATH"]
    ?? Path.Combine(builder.Environment.ContentRootPath, "App_Data", "keys"),
    builder.Environment.ContentRootPath);
Directory.CreateDirectory(keysPath);
builder.Services.AddDataProtection()
    .SetApplicationName("TitanicSafetyApp")
    .PersistKeysToFileSystem(new DirectoryInfo(keysPath));

builder.Services.AddRazorComponents().AddInteractiveServerComponents();
builder.Services.AddHttpClient("TitanicApi", client =>
{
    client.BaseAddress = apiBaseUri;
    client.Timeout = TimeSpan.FromSeconds(8);
});
builder.Services.AddScoped<ITitanicApiClient, TitanicApiClient>();

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    app.UseHsts();
}

app.UseStaticFiles();
app.UseAntiforgery();
app.MapRazorComponents<App>().AddInteractiveServerRenderMode();

app.Run();
