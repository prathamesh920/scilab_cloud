mode(2);
//Chapter 2
//Example 2.1 
//Page 21
clear;clc;
E1=100+0*%i;
E2=86.6+50*%i;
Z=5*%i;
X=5;
printf("\n\n Value of voltage source one designated as a machine 1 =  %.4f V \n\n",E1)
printf("\n\n Value of voltage source two designated as a machine 2 =  %.4f V \n\n",E2)
printf("\n\n Impedance connected  = %.4f ohms \n\n",abs(Z))


//Calculation Of Current
I=(E1-E2)/Z;
printf("\n\n Current through the impedance = %.4f A \n\n",I)


//Calculation Of Power
M1=E1*conj(I);
disp(M1,'Machine One Power = ')
M2=E2*conj(I);
disp(M2,'Machine Two Power = ')


//Calculation Of Reactive Power Required By Inductive Reactance
RP=(abs(I))^2*X;
printf("\n\n Reactive power required by inductive reactance i.e, impedance = %.4f VAR \n\n",RP)
printf("\n\n Machine 1 consumes energy at the rate of %.4f W \n\n",abs(real(M1)))
printf("\n\n Machine 2 generates energy at the rate of %.4f W \n\n",abs(real(M2)))
printf("\n\n Machine 1 supplies reactive power at the rate of  %.4f VAR \n\n",imag(M1))
printf("\n\n Machine 2 supplies reactive power at the rate of %.4f VAR \n\n",abs(imag(M2)))
printf("\n\n Reactive power required by inductive reactance i.e, impedance = Sum of reactive power supplied by machine 1 + reactive power supplied by machine 2  = %.4f VAR \n\n",RP)
disp('Real Power consumed by impedance is Zero')
disp('The real power generated by machine two is transferred to machine one')

quit;