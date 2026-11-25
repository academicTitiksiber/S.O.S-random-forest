using System.ComponentModel.DataAnnotations;

namespace TitanicSafetyApp.Models;

public sealed class PassengerFormModel
{
    [Range(1, 3, ErrorMessage = "Kelas penumpang harus 1, 2, atau 3.")]
    public int Pclass { get; set; } = 1;

    [RegularExpression("^(male|female)$", ErrorMessage = "Jenis kelamin harus male atau female.")]
    public string Sex { get; set; } = "male";

    [Range(0.1, 100, ErrorMessage = "Usia harus antara 0,1 sampai 100 tahun.")]
    public double Age { get; set; } = 30;

    [Range(0, 20, ErrorMessage = "Jumlah saudara/pasangan harus 0 sampai 20.")]
    public int SibSp { get; set; }

    [Range(0, 20, ErrorMessage = "Jumlah orang tua/anak harus 0 sampai 20.")]
    public int Parch { get; set; }

    [Range(0.0, 1000, ErrorMessage = "Tarif harus antara 0 sampai 1000.")]
    public double Fare { get; set; } = 50;

    [RegularExpression("^(S|C|Q)$", ErrorMessage = "Pelabuhan keberangkatan harus S, C, atau Q.")]
    public string Embarked { get; set; } = "S";

    [RegularExpression("^(Mr|Mrs|Miss|Master|Rare)$", ErrorMessage = "Gelar tidak dikenali.")]
    public string Title { get; set; } = "Mr";

    public bool HasCabin { get; set; }

    public PredictionRequest ToRequest() => new()
    {
        Pclass = Pclass,
        Sex = Sex,
        Age = Age,
        SibSp = SibSp,
        Parch = Parch,
        Fare = Fare,
        Embarked = Embarked,
        Title = Title,
        HasCabin = HasCabin ? 1 : 0
    };
}
