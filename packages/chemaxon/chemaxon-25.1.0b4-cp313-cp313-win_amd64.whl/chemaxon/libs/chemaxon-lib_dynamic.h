#ifndef __CHEMAXON_LIB_H
#define __CHEMAXON_LIB_H

#include <graal_isolate_dynamic.h>


#if defined(__cplusplus)
extern "C" {
#endif

typedef fingerprint* (*cfp_fn_t)(graal_isolatethread_t*, molecule*, int, int, int, int);

typedef void (*free_cfp_fn_t)(graal_isolatethread_t*);

typedef charge_result* (*charge_fn_t)(graal_isolatethread_t*, molecule*);

typedef void (*free_charge_result_fn_t)(graal_isolatethread_t*);

typedef string_result* (*chemterm_fn_t)(graal_isolatethread_t*, molecule*, char*);

typedef void (*free_chemterm_result_fn_t)(graal_isolatethread_t*);

typedef double_result* (*tanimoto_fn_t)(graal_isolatethread_t*, long long*, long long*, int);

typedef double_result* (*float_vector_tanimoto_fn_t)(graal_isolatethread_t*, float*, float*, int);

typedef void (*free_tanimoto_result_fn_t)(graal_isolatethread_t*);

typedef fingerprint* (*ecfp_fn_t)(graal_isolatethread_t*, molecule*, int, int);

typedef fingerprint* (*fcfp_fn_t)(graal_isolatethread_t*, molecule*, int, int);

typedef void (*free_ecfp_fn_t)(graal_isolatethread_t*);

typedef double_result* (*hlb_fn_t)(graal_isolatethread_t*, molecule*, hlb_method);

typedef void (*free_hlb_result_fn_t)(graal_isolatethread_t*);

typedef char* (*ccl_version_fn_t)(graal_isolatethread_t*);

typedef void (*free_ccl_version_fn_t)(graal_isolatethread_t*);

typedef char* (*ccl_build_date_fn_t)(graal_isolatethread_t*);

typedef void (*free_ccl_build_date_fn_t)(graal_isolatethread_t*);

typedef char* (*licenses_fn_t)(graal_isolatethread_t*);

typedef void (*free_licenses_fn_t)(graal_isolatethread_t*);

typedef char* (*charset_test_fn_t)(graal_isolatethread_t*);

typedef void (*free_charsets_fn_t)(graal_isolatethread_t*);

typedef double_result* (*logD_fn_t)(graal_isolatethread_t*, molecule*, double, logp_method, int);

typedef void (*free_logd_result_fn_t)(graal_isolatethread_t*);

typedef logp_result* (*logP_fn_t)(graal_isolatethread_t*, molecule*, logp_method, double, double, int, double, int);

typedef void (*free_logp_result_fn_t)(graal_isolatethread_t*);

typedef molecule* (*major_microspecies_fn_t)(graal_isolatethread_t*, molecule*, double, int, int);

typedef void (*free_major_microspecies_result_fn_t)(graal_isolatethread_t*);

typedef string_result* (*export_mol_fn_t)(graal_isolatethread_t*, molecule*, char*);

typedef void (*free_export_mol_result_fn_t)(graal_isolatethread_t*);

typedef molecule* (*import_mol_fn_t)(graal_isolatethread_t*, char*, char*);

typedef void (*free_import_mol_result_fn_t)(graal_isolatethread_t*);

typedef float_vector_fingerprint* (*pharmacophore_fp_fn_t)(graal_isolatethread_t*, molecule*);

typedef void (*free_fp_result_fn_t)(graal_isolatethread_t*);

typedef pka_result* (*pka_fn_t)(graal_isolatethread_t*, molecule*);

typedef void (*free_pka_result_fn_t)(graal_isolatethread_t*);

typedef polarizability_result* (*polarizability_fn_t)(graal_isolatethread_t*, molecule*, double, int);

typedef void (*free_polarizability_result_fn_t)(graal_isolatethread_t*);

typedef molecule* (*standardize_fn_t)(graal_isolatethread_t*, molecule*, char*);

typedef void (*free_standardized_molecule_fn_t)(graal_isolatethread_t*);

typedef structurechecker_batch_result* (*check_fn_t)(graal_isolatethread_t*, molecule*, char*, int);

typedef void (*free_structurechecker_result_fn_t)(graal_isolatethread_t*);

typedef structurefixer_result* (*fix_fn_t)(graal_isolatethread_t*, molecule*, char*);

typedef void (*free_fixer_result_fn_t)(graal_isolatethread_t*);

#if defined(__cplusplus)
}
#endif
#endif
