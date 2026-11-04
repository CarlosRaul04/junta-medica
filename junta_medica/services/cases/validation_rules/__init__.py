"""
Reglas de validación de casos (todas implementan interfaces.validation_rule.ValidationRule):
    field_rules.py      -> RequiredFields, AllowedFields, FieldTypes, IdentifierFormat
    clinical_rules.py    -> AgeRange, ValidSex, RecognizedLabTests
    privacy_rules.py  -> NoPersonalData (RF03)
Para agregar una regla: crear la clase en el archivo que corresponda y sumarla en factories/case_factory.py.
"""
