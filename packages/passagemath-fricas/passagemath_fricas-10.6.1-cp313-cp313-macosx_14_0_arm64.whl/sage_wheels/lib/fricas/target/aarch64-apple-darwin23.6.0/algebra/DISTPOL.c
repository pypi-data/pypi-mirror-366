/*      Compiler: ECL 24.5.10                                         */
/*      Date: 2025/7/31 09:08 (yyyy/mm/dd)                            */
/*      Machine: Darwin 23.6.0 arm64                                  */
/*      Source: /Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/pre-generated/src/algebra/DISTPOL.lsp */
#include <ecl/ecl-cmp.h>
#include "/Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/_build/target/aarch64-apple-darwin23.6.0/algebra/DISTPOL.eclh"
/*      function definition for DISTPOL;eval;DUPSS;1                  */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L529_distpol_eval_dupss_1_(cl_object v1_x_, cl_object v2_p_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5, T6, T7;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_res_;
  v4_res_ = ECL_NIL;
  {
   cl_object v5;
   v5 = (v3_)->vector.self.t[10];
   T0 = _ecl_car(v5);
   T1 = _ecl_cdr(v5);
   if (Null((cl_env_copy->function=T0)->cfun.entry(2, v2_p_, T1))) { goto L3; }
  }
  {
   cl_object v5;
   v5 = (v3_)->vector.self.t[13];
   T0 = _ecl_car(v5);
   {
    cl_object v6;
    v6 = (v3_)->vector.self.t[11];
    T2 = _ecl_car(v6);
    T3 = _ecl_cdr(v6);
    T1 = (cl_env_copy->function=T2)->cfun.entry(2, v2_p_, T3);
   }
   {
    cl_object v6;
    v6 = (v3_)->vector.self.t[12];
    T3 = _ecl_car(v6);
    T4 = _ecl_cdr(v6);
    T2 = (cl_env_copy->function=T3)->cfun.entry(1, T4);
   }
   T3 = _ecl_cdr(v5);
   value0 = (cl_env_copy->function=T0)->cfun.entry(3, T1, T2, T3);
   return value0;
  }
L3:;
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[14];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v4_res_ = (cl_env_copy->function=T0)->cfun.entry(1, T1);
  }
L20:;
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[15];
   T1 = _ecl_car(v6);
   T2 = _ecl_cdr(v6);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v2_p_, T2);
  }
  {
   bool v6;
   v6 = T0==ECL_NIL;
   if (!(ecl_make_bool(v6)==ECL_NIL)) { goto L22; }
  }
  goto L21;
L22:;
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[21];
   T0 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v3_)->vector.self.t[20];
    T2 = _ecl_car(v7);
    {
     cl_object v8;
     v8 = (v3_)->vector.self.t[19];
     T4 = _ecl_car(v8);
     {
      cl_object v9;
      v9 = (v3_)->vector.self.t[17];
      T6 = _ecl_car(v9);
      T7 = _ecl_cdr(v9);
      T5 = (cl_env_copy->function=T6)->cfun.entry(2, v2_p_, T7);
     }
     T6 = _ecl_cdr(v8);
     T3 = (cl_env_copy->function=T4)->cfun.entry(3, v1_x_, T5, T6);
    }
    {
     cl_object v8;
     v8 = (v3_)->vector.self.t[11];
     T5 = _ecl_car(v8);
     T6 = _ecl_cdr(v8);
     T4 = (cl_env_copy->function=T5)->cfun.entry(2, v2_p_, T6);
    }
    T5 = _ecl_cdr(v7);
    T1 = (cl_env_copy->function=T2)->cfun.entry(3, T3, T4, T5);
   }
   T2 = _ecl_cdr(v6);
   v4_res_ = (cl_env_copy->function=T0)->cfun.entry(3, v4_res_, T1, T2);
  }
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[22];
   T0 = _ecl_car(v6);
   T1 = _ecl_cdr(v6);
   v2_p_ = (cl_env_copy->function=T0)->cfun.entry(2, v2_p_, T1);
  }
  goto L27;
L27:;
  goto L20;
L21:;
  goto L19;
L19:;
  value0 = v4_res_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for DISTPOL;integrate;UPSDS;2             */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L530_distpol_integrate_upsds_2_(cl_object v1_p_, cl_object v2_x_, cl_object v3_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[23];
  T0 = _ecl_car(v4);
  T1 = _ecl_cdr(v4);
  value0 = (cl_env_copy->function=T0)->cfun.entry(3, v2_x_, v1_p_, T1);
  return value0;
 }
}
/*      function definition for DISTPOL;apply;UPSDD;3                 */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L531_distpol_apply_upsdd_3_(cl_object v1_p_, cl_object v2_x_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_mompx_;
  cl_object v5in;
  v4_mompx_ = ECL_NIL;
  v5in = ECL_NIL;
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[31];
   T0 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v3_)->vector.self.t[28];
    T2 = _ecl_car(v7);
    T3 = _ecl_cdr(v7);
    T1 = (cl_env_copy->function=T2)->cfun.entry(2, ecl_make_fixnum(1), T3);
   }
   T2 = ecl_list1(T1);
   T3 = _ecl_cdr(v6);
   v5in = (cl_env_copy->function=T0)->cfun.entry(2, T2, T3);
  }
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[37];
   T0 = _ecl_car(v6);
   T1 = (VV[3]->symbol.gfdef);
   T2 = cl_vector(3, v3_, v1_p_, v2_x_);
   T3 = CONS(T1,T2);
   T4 = _ecl_cdr(v6);
   v4_mompx_ = (cl_env_copy->function=T0)->cfun.entry(3, T3, v5in, T4);
  }
  {
   cl_object v6;
   v6 = (v3_)->vector.self.t[41];
   T0 = _ecl_car(v6);
   {
    cl_object v7;
    v7 = (v3_)->vector.self.t[39];
    T2 = _ecl_car(v7);
    T3 = _ecl_cdr(v7);
    T1 = (cl_env_copy->function=T2)->cfun.entry(2, v4_mompx_, T3);
   }
   T2 = _ecl_cdr(v6);
   value0 = (cl_env_copy->function=T0)->cfun.entry(2, T1, T2);
   return value0;
  }
 }
}
/*      function definition for DISTPOL;apply;UPSDD;3!0               */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L532_distpol_apply_upsdd_3_0_(cl_object v1_k_, cl_object v2__)
{
 cl_object T0, T1, T2, T3, T4;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3_x_;
  cl_object v4_p_;
  cl_object v5_;
  v3_x_ = ECL_NIL;
  v4_p_ = ECL_NIL;
  v5_ = ECL_NIL;
  v3_x_ = (v2__)->vector.self.t[2];
  v4_p_ = (v2__)->vector.self.t[1];
  v5_ = (v2__)->vector.self.t[0];
  {
   cl_object v6;
   v6 = ECL_NIL;
   {
    cl_object v7;
    v7 = (v5_)->vector.self.t[23];
    T0 = _ecl_car(v7);
    {
     cl_object v8;
     v8 = (v5_)->vector.self.t[33];
     T2 = _ecl_car(v8);
     {
      cl_object v9;
      v6 = v1_k_;
      v9 = v6;
      {
       bool v10;
       v10 = ecl_greater(v6,ecl_make_fixnum(0));
       if (!(ecl_make_bool(v10)==ECL_NIL)) { goto L20; }
      }
      T4 = ecl_function_dispatch(cl_env_copy,VV[16])(3, v6, VV[4], VV[5]) /*  coerce_failure_msg */;
      ecl_function_dispatch(cl_env_copy,VV[17])(1, T4) /*  error      */;
L20:;
      T3 = v9;
     }
     T4 = _ecl_cdr(v8);
     T1 = (cl_env_copy->function=T2)->cfun.entry(3, v4_p_, T3, T4);
    }
    T2 = _ecl_cdr(v7);
    value0 = (cl_env_copy->function=T0)->cfun.entry(3, v3_x_, T1, T2);
    return value0;
   }
  }
 }
}
/*      function definition for DistributionPolynomialPackage;        */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L533_distributionpolynomialpackage__(cl_object v1__1_, cl_object v2__2_, cl_object v3__3_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4_pv__;
  cl_object v5_;
  cl_object v6_dv__;
  cl_object v7dv_3;
  cl_object v8dv_2;
  cl_object v9dv_1;
  v4_pv__ = ECL_NIL;
  v5_ = ECL_NIL;
  v6_dv__ = ECL_NIL;
  v7dv_3 = ECL_NIL;
  v8dv_2 = ECL_NIL;
  v9dv_1 = ECL_NIL;
  v9dv_1 = ecl_function_dispatch(cl_env_copy,VV[19])(1, v1__1_) /*  devaluate */;
  v8dv_2 = ecl_function_dispatch(cl_env_copy,VV[19])(1, v2__2_) /*  devaluate */;
  v7dv_3 = ecl_function_dispatch(cl_env_copy,VV[19])(1, v3__3_) /*  devaluate */;
  v6_dv__ = cl_list(4, VV[7], v9dv_1, v8dv_2, v7dv_3);
  v5_ = ecl_function_dispatch(cl_env_copy,VV[20])(1, ecl_make_fixnum(43)) /*  GETREFV */;
  (v5_)->vector.self.t[0]= v6_dv__;
  v4_pv__ = ecl_function_dispatch(cl_env_copy,VV[21])(3, ecl_make_fixnum(0), ecl_make_fixnum(0), ECL_NIL) /*  buildPredVector */;
  (v5_)->vector.self.t[3]= v4_pv__;
  T0 = cl_list(3, v9dv_1, v8dv_2, v7dv_3);
  T1 = CONS(ecl_make_fixnum(1),v5_);
  ecl_function_dispatch(cl_env_copy,VV[22])(4, ECL_SYM_VAL(cl_env_copy,VV[8]), VV[7], T0, T1) /*  haddProp */;
  ecl_function_dispatch(cl_env_copy,VV[23])(1, v5_) /*  stuffDomainSlots */;
  (v5_)->vector.self.t[6]= v1__1_;
  (v5_)->vector.self.t[7]= v2__2_;
  (v5_)->vector.self.t[8]= v3__3_;
  v4_pv__ = (v5_)->vector.self.t[3];
  value0 = v5_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for DistributionPolynomialPackage         */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L534_distributionpolynomialpackage_(volatile cl_narg narg, ...)
{
 cl_object T0, T1;
 cl_object volatile env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object volatile value0;
 cl_object volatile v1;
 ecl_va_list args; ecl_va_start(args,narg,narg,0);
 v1 = cl_grab_rest_args(args);
 ecl_va_end(args);
 {
  volatile cl_object v2;
  v2 = ECL_NIL;
  T0 = ecl_function_dispatch(cl_env_copy,VV[25])(1, v1) /*  devaluateList */;
  T1 = ecl_gethash_safe(VV[7],ECL_SYM_VAL(cl_env_copy,VV[8]),ECL_NIL);
  v2 = ecl_function_dispatch(cl_env_copy,VV[26])(3, T0, T1, VV[9]) /*  lassocShiftWithFunction */;
  if (Null(v2)) { goto L3; }
  value0 = ecl_function_dispatch(cl_env_copy,VV[27])(1, v2) /*  CDRwithIncrement */;
  return value0;
L3:;
  {
   volatile bool unwinding = FALSE;
   cl_index v3=ECL_STACK_INDEX(cl_env_copy),v4;
   ecl_frame_ptr next_fr;
   ecl_frs_push(cl_env_copy,ECL_PROTECT_TAG);
   if (__ecl_frs_push_result) {
     unwinding = TRUE; next_fr=cl_env_copy->nlj_fr;
   } else {
   {
    cl_object v5;
    T0 = (VV[6]->symbol.gfdef);
    v5 = cl_apply(2, T0, v1);
    v2 = ECL_T;
    cl_env_copy->values[0] = v5;
    cl_env_copy->nvalues = 1;
   }
   }
   ecl_frs_pop(cl_env_copy);
   v4=ecl_stack_push_values(cl_env_copy);
   if ((v2)!=ECL_NIL) { goto L11; }
   cl_remhash(VV[7], ECL_SYM_VAL(cl_env_copy,VV[8]));
L11:;
   ecl_stack_pop_values(cl_env_copy,v4);
   if (unwinding) ecl_unwind(cl_env_copy,next_fr);
   ECL_STACK_SET_INDEX(cl_env_copy,v3);
   return cl_env_copy->values[0];
  }
 }
}