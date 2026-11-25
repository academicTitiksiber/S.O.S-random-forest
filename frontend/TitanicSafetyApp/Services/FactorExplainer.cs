using TitanicSafetyApp.Models;

namespace TitanicSafetyApp.Services;

public sealed record FactorInsight(string Title, string Description, bool SupportsSurvival);

public static class FactorExplainer
{
    public static IReadOnlyList<FactorInsight> Explain(PassengerFormModel passenger)
    {
        var insights = new List<FactorInsight>();
        var familySize = passenger.SibSp + passenger.Parch + 1;

        if (passenger.Pclass == 1)
        {
            insights.Add(new FactorInsight(
                "Kelas 1",
                "Penumpang kelas pertama memiliki akses lebih awal ke sekoci.",
                true));
        }
        else if (passenger.Pclass == 3)
        {
            insights.Add(new FactorInsight(
                "Kelas 3",
                "Penumpang kelas ketiga secara historis memiliki tingkat keselamatan lebih rendah.",
                false));
        }

        if (passenger.Sex == "female")
        {
            insights.Add(new FactorInsight(
                "Jenis kelamin",
                "Kebijakan evakuasi 'women and children first' menguntungkan perempuan.",
                true));
        }
        else
        {
            insights.Add(new FactorInsight(
                "Jenis kelamin",
                "Pria memiliki peluang selamat lebih rendah dalam data historis Titanic.",
                false));
        }

        if (passenger.HasCabin)
        {
            insights.Add(new FactorInsight(
                "Data kabin tersedia",
                "Nomor kabin penumpang tercatat dalam data keberangkatan.",
                true));
        }

        if (passenger.Title is "Master" or "Miss")
        {
            insights.Add(new FactorInsight(
                $"Gelar {passenger.Title}",
                "Gelar ini sering menandakan anak-anak, yang diprioritaskan saat evakuasi.",
                true));
        }

        if (familySize == 1)
        {
            insights.Add(new FactorInsight(
                "Bepergian sendiri",
                "Penumpang tanpa keluarga kehilangan bantuan saat evakuasi.",
                false));
        }
        else if (familySize <= 4)
        {
            insights.Add(new FactorInsight(
                $"Keluarga kecil ({familySize} orang)",
                "Ukuran keluarga sedang cenderung membantu proses evakuasi.",
                true));
        }
        else
        {
            insights.Add(new FactorInsight(
                $"Keluarga besar ({familySize} orang)",
                "Keluarga besar lebih sulit bergerak bersama menuju sekoci.",
                false));
        }

        if (passenger.Age < 12)
        {
            insights.Add(new FactorInsight(
                "Usia di bawah 12 tahun",
                "Anak-anak termasuk kelompok yang diprioritaskan.",
                true));
        }

        return insights.Take(4).ToList();
    }
}
