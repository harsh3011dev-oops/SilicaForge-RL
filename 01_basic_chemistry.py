import cantera as ct

# 1. Physics Engine Load Karna
# 'gri30.yaml' Cantera ka ek default dataset hai jisme saari common gases ki details hoti hain.
gas = ct.Solution('gri30.yaml')

# 2. Initial State Define Karna
# T = Temperature (Kelvin mein) -> 300 K (lagbhag room temperature)
# P = Pressure -> 1 atm
# X = Mixture -> Hum 1 hissa Methane (CH4) aur 2 hisse Oxygen (O2) mila rahe hain
gas.TPX = 300.0, ct.one_atm, 'CH4:1, O2:2'

print("--- REACTION SE PEHLE ---")
print(f"Temperature: {gas.T} K")
print(f"Methane (CH4) = {gas['CH4'].X[0]:.3f}")
print(f"Oxygen (O2) = {gas['O2'].X[0]:.3f}")
print(f"Carbon Dioxide (CO2) = {gas['CO2'].X[0]:.3f}") # Reaction se pehle CO2 zero hoga

# 3. Asli Jadoo Yahan Hota Hai: Equilibrate
# 'TP' ka matlab hai ki hum Temperature aur Pressure ko constant rakh rahe hain.
# Yeh function wahi "Gibbs Free Energy" minimize karega jo maine bataya tha.
gas.equilibrate('TP')

print("\n--- REACTION KE BAAD (Equilibrium) ---")
print("Nature ne apne aap energy minimize karke naye chemicals bana diye:")
print(f"Temperature: {gas.T} K")
print(f"Carbon Dioxide (CO2) = {gas['CO2'].X[0]:.3f}")
print(f"Water vapor (H2O) = {gas['H2O'].X[0]:.3f}")
print(f"Bachi hui Methane (CH4) = {gas['CH4'].X[0]:.3e} (Bohot kam)")
