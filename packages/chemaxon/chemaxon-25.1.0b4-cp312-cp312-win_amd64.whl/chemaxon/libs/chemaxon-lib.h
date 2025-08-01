#ifndef __CHEMAXON_LIB_H
#define __CHEMAXON_LIB_H

#include <graal_isolate.h>


#if defined(__cplusplus)
extern "C" {
#endif

fingerprint* cfp(graal_isolatethread_t*, molecule*, int, int, int, int);

void free_cfp(graal_isolatethread_t*);

charge_result* charge(graal_isolatethread_t*, molecule*);

void free_charge_result(graal_isolatethread_t*);

string_result* chemterm(graal_isolatethread_t*, molecule*, char*);

void free_chemterm_result(graal_isolatethread_t*);

double_result* tanimoto(graal_isolatethread_t*, long long*, long long*, int);

double_result* float_vector_tanimoto(graal_isolatethread_t*, float*, float*, int);

void free_tanimoto_result(graal_isolatethread_t*);

fingerprint* ecfp(graal_isolatethread_t*, molecule*, int, int);

fingerprint* fcfp(graal_isolatethread_t*, molecule*, int, int);

void free_ecfp(graal_isolatethread_t*);

double_result* hlb(graal_isolatethread_t*, molecule*, hlb_method);

void free_hlb_result(graal_isolatethread_t*);

char* ccl_version(graal_isolatethread_t*);

void free_ccl_version(graal_isolatethread_t*);

char* ccl_build_date(graal_isolatethread_t*);

void free_ccl_build_date(graal_isolatethread_t*);

char* licenses(graal_isolatethread_t*);

void free_licenses(graal_isolatethread_t*);

char* charset_test(graal_isolatethread_t*);

void free_charsets(graal_isolatethread_t*);

double_result* logD(graal_isolatethread_t*, molecule*, double, logp_method, int);

void free_logd_result(graal_isolatethread_t*);

logp_result* logP(graal_isolatethread_t*, molecule*, logp_method, double, double, int, double, int);

void free_logp_result(graal_isolatethread_t*);

molecule* major_microspecies(graal_isolatethread_t*, molecule*, double, int, int);

void free_major_microspecies_result(graal_isolatethread_t*);

string_result* export_mol(graal_isolatethread_t*, molecule*, char*);

void free_export_mol_result(graal_isolatethread_t*);

molecule* import_mol(graal_isolatethread_t*, char*, char*);

void free_import_mol_result(graal_isolatethread_t*);

float_vector_fingerprint* pharmacophore_fp(graal_isolatethread_t*, molecule*);

void free_fp_result(graal_isolatethread_t*);

pka_result* pka(graal_isolatethread_t*, molecule*);

void free_pka_result(graal_isolatethread_t*);

polarizability_result* polarizability(graal_isolatethread_t*, molecule*, double, int);

void free_polarizability_result(graal_isolatethread_t*);

molecule* standardize(graal_isolatethread_t*, molecule*, char*);

void free_standardized_molecule(graal_isolatethread_t*);

structurechecker_batch_result* check(graal_isolatethread_t*, molecule*, char*, int);

void free_structurechecker_result(graal_isolatethread_t*);

structurefixer_result* fix(graal_isolatethread_t*, molecule*, char*);

void free_fixer_result(graal_isolatethread_t*);

#if defined(__cplusplus)
}
#endif
#endif
