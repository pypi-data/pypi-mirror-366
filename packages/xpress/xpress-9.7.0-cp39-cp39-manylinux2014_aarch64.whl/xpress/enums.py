import enum

class SolStatus(enum.IntEnum):
  NOTFOUND   = 0
  OPTIMAL    = 1
  FEASIBLE   = 2
  INFEASIBLE = 3
  UNBOUNDED  = 4

class SolveStatus(enum.IntEnum):
  UNSTARTED = 0
  STOPPED   = 1
  FAILED    = 2
  COMPLETED = 3

class LPStatus(enum.IntEnum):
  UNSTARTED      = 0
  OPTIMAL        = 1
  INFEAS         = 2
  CUTOFF         = 3
  UNFINISHED     = 4
  UNBOUNDED      = 5
  CUTOFF_IN_DUAL = 6
  UNSOLVED       = 7
  NONCONVEX      = 8

class MIPStatus(enum.IntEnum):
  NOT_LOADED     = 0
  LP_NOT_OPTIMAL = 1
  LP_OPTIMAL     = 2
  NO_SOL_FOUND   = 3
  SOLUTION       = 4
  INFEAS         = 5
  OPTIMAL        = 6
  UNBOUNDED      = 7

class IISSolStatus(enum.IntEnum):
  UNSTARTED  = 0
  FEASIBLE   = 1
  COMPLETED  = 2
  UNFINISHED = 3

class SolAvailable(enum.IntEnum):
  NOTFOUND = 0
  OPTIMAL  = 1
  FEASIBLE = 2

class OptimizeType(enum.IntEnum):
  NONE   = -1
  LP     = 0
  MIP    = 1
  LOCAL  = 2
  GLOBAL = 3

class BarOrder(enum.IntEnum):
  DEFAULT           = 0
  MIN_DEGREE        = 1
  MIN_LOCAL_FILL    = 2
  NESTED_DISSECTION = 3

class DefaultAlg(enum.IntEnum):
  DEFAULT = 1
  DUAL    = 2
  PRIMAL  = 3
  BARRIER = 4
  NETWORK = 5

class StopType(enum.IntEnum):
  NONE           = 0
  TIMELIMIT      = 1
  CTRLC          = 2
  NODELIMIT      = 3
  ITERLIMIT      = 4
  MIPGAP         = 5
  SOLLIMIT       = 6
  GENERICERROR   = 7
  MEMORYERROR    = 8
  USER           = 9
  SOLVECOMPLETE  = 10
  LICENSELOST    = 11
  NUMERICALERROR = 13
  WORKLIMIT      = 14

class AlwaysNeverAutomatic(enum.IntEnum):
  AUTOMATIC = -1
  NEVER     = 0
  ALWAYS    = 1

class OnOff(enum.IntEnum):
  OFF = 0
  ON  = 1

class BacktrackAlg(enum.IntEnum):
  BEST_ESTIMATE            = 2
  BEST_BOUND               = 3
  DEEPEST_NODE             = 4
  HIGHEST_NODE             = 5
  EARLIEST_NODE            = 6
  LATEST_NODE              = 7
  RANDOM                   = 8
  MIN_INFEAS               = 9
  BEST_ESTIMATE_MIN_INFEAS = 10
  DEEPEST_BEST_ESTIMATE    = 11

class BranchChoice(enum.IntEnum):
  MIN_EST_FIRST = 0
  MAX_EST_FIRST = 1

class CholeskyAlgorithm(enum.IntEnum):
  PULL_CHOLESKY = 0
  PUSH_CHOLESKY = 1

class CrossoverDynamicReduction(enum.IntEnum):
  BEFORE_CROSSOVER            = 1
  INSIDE_CROSSOVER            = 2
  AGGRESSIVE_BEFORE_CROSSOVER = 4

class DualGradient(enum.IntEnum):
  AUTOMATIC    = -1
  DEVEX        = 0
  STEEPESTEDGE = 1

class DualStrategy(enum.IntEnum):
  REMOVE_INFEAS_WITH_PRIMAL = 0
  REMOVE_INFEAS_WITH_DUAL   = 1

class FeasibilityPump(enum.IntEnum):
  AUTOMATIC  = -1
  NEVER      = 0
  ALWAYS     = 1
  LASTRESORT = 2

class HeuristicSearchSelect(enum.IntEnum):
  LOCAL_SEARCH_LARGE_NEIGHBOURHOOD    = 0
  LOCAL_SEARCH_NODE_NEIGHBOURHOOD     = 1
  LOCAL_SEARCH_SOLUTION_NEIGHBOURHOOD = 2

class NodeSelectionCriteria(enum.IntEnum):
  LOCAL_FIRST                 = 1
  BEST_FIRST                  = 2
  LOCAL_DEPTH_FIRST           = 3
  BEST_FIRST_THEN_LOCAL_FIRST = 4
  DEPTH_FIRST                 = 5

class OutputDetail(enum.IntEnum):
  NO_OUTPUT           = 0
  FULL_OUTPUT         = 1
  ERRORS_AND_WARNINGS = 3
  ERRORS              = 4

class PreProbing(enum.IntEnum):
  AUTOMATIC       = -1
  DISABLED        = 0
  LIGHT           = 1
  FULL            = 2
  FULL_AND_REPEAT = 3

class PresolveOperations(enum.IntEnum):
  SINGLETONCOLUMNREMOVAL           = 1
  SINGLETONROWREMOVAL              = 2
  FORCINGROWREMOVAL                = 4
  DUALREDUCTIONS                   = 8
  REDUNDANTROWREMOVAL              = 16
  DUPLICATECOLUMNREMOVAL           = 32
  DUPLICATEROWREMOVAL              = 64
  STRONGDUALREDUCTIONS             = 128
  VARIABLEELIMINATIONS             = 256
  NOIPREDUCTIONS                   = 512
  NOGLOBALDOMAINCHANGE             = 1024
  NOADVANCEDIPREDUCTIONS           = 2048
  NOINTEGERELIMINATIONS            = 4096
  NOSOLUTIONENUMERATION            = 8192
  LINEARLYDEPENDANTROWREMOVAL      = 16384
  NOINTEGERVARIABLEANDSOSDETECTION = 32768
  NOIMPLIEDBOUNDS                  = 65536
  NOCLIQUEPRESOLVE                 = 131072
  NOMOD2REDUCTIONS                 = 262144
  NODUALREDONGLOBALS               = 536870912

class PresolveState(enum.IntEnum):
  PROBLEMLOADED       = 1
  PROBLEMLPPRESOLVED  = 2
  PROBLEMMIPPRESOLVED = 4
  SOLUTIONVALID       = 128

class MipPresolve(enum.IntEnum):
  REDUCED_COST_FIXING           = 1
  LOGIC_PREPROCESSING           = 2
  ALLOW_CHANGE_BOUNDS           = 8
  DUAL_REDUCTIONS               = 16
  GLOBAL_COEFFICIENT_TIGHTENING = 32
  OBJECTIVE_BASED_REDUCTIONS    = 64
  ALLOW_TREE_RESTART            = 128
  SYMMETRY_REDUCTIONS           = 256

class Presolve(enum.IntEnum):
  NOPRIMALINFEASIBILITY = -1
  NONE                  = 0
  DEFAULT               = 1
  KEEPREDUNDANTBOUNDS   = 2

class Pricing(enum.IntEnum):
  PARTIAL = -1
  DEFAULT = 0
  DEVEX   = 1

class CutStrategy(enum.IntEnum):
  DEFAULT      = -1
  NONE         = 0
  CONSERVATIVE = 1
  MODERATE     = 2
  AGGRESSIVE   = 3

class VariableSelection(enum.IntEnum):
  AUTOMATIC                              = -1
  MIN_UPDOWN_PSEUDO_COSTS                = 1
  SUM_UPDOWN_PSEUDO_COSTS                = 2
  MAX_UPDOWN_PSEUDO_COSTS_PLUS_TWICE_MIN = 3
  MAX_UPDOWN_PSEUDO_COSTS                = 4
  DOWN_PSEUDO_COST                       = 5
  UP_PSEUDO_COST                         = 6

class Scaling(enum.IntEnum):
  ROW_SCALING                      = 1
  COLUMN_SCALING                   = 2
  ROW_SCALING_AGAIN                = 4
  MAXIMUM                          = 8
  CURTIS_REID                      = 16
  BY_MAX_ELEM_NOT_GEO_MEAN         = 32
  BIGM                             = 64
  SIMPLEX_OBJECTIVE_SCALING        = 128
  IGNORE_QUADRATIC_ROW_PART        = 256
  BEFORE_PRESOLVE                  = 512
  NO_SCALING_ROWS_UP               = 1024
  NO_SCALING_COLUMNS_DOWN          = 2048
  DISABLE_GLOBAL_OBJECTIVE_SCALING = 4096
  RHS_SCALING                      = 8192
  NO_AGGRESSIVE_Q_SCALING          = 16384
  SLACK_SCALING                    = 32768
  RUIZ                             = 65536
  DOGLEG                           = 131072
  BEFORE_AND_AFTER_PRESOLVE        = 262144

class CutSelect(enum.IntEnum):
  CLIQUE           = 1855
  MIR              = 1887
  COVER            = 1951
  FLOWPATH         = 3871
  IMPLICATION      = 5919
  LIFT_AND_PROJECT = 10015
  DISABLE_CUT_ROWS = 18207
  GUB_COVER        = 34591
  DEFAULT          = -1

class RefineOps(enum.IntEnum):
  LPOPTIMAL           = 1
  MIPSOLUTION         = 2
  MIPNODELP           = 8
  LPPRESOLVE          = 16
  ITERATIVEREFINER    = 32
  REFINERPRECISION    = 64
  REFINERUSEPRIMAL    = 128
  REFINERUSEDUAL      = 256
  MIPFIXGLOBALS       = 512
  MIPFIXGLOBALSTARGET = 1024

class DualizeOps(enum.IntEnum):
  SWITCHALGORITHM = 1

class TreeDiagnostics(enum.IntEnum):
  MEMORY_USAGE_SUMMARIES = 1
  MEMORY_SAVED_REPORTS   = 2

class BarPresolveOps(enum.IntEnum):
  STANDARD_PRESOLVE      = 0
  EXTRA_BARRIER_PRESOLVE = 1

class MipRestart(enum.IntEnum):
  DEFAULT    = -1
  OFF        = 0
  MODERATE   = 1
  AGGRESSIVE = 2

class PresolveCoefElim(enum.IntEnum):
  DISABLED   = 0
  AGGRESSIVE = 1
  CAUTIOUS   = 2

class PresolveDomRow(enum.IntEnum):
  AUTOMATIC  = -1
  DISABLED   = 0
  CAUTIOUS   = 1
  MEDIUM     = 2
  AGGRESSIVE = 3

class PresolveDomColumn(enum.IntEnum):
  AUTOMATIC  = -1
  DISABLED   = 0
  CAUTIOUS   = 1
  AGGRESSIVE = 2

class PrimalUnshift(enum.IntEnum):
  ALLOW_DUAL_UNSHIFT = 0
  NO_DUAL_UNSHIFT    = 1

class RepairIndefiniteQuadratic(enum.IntEnum):
  REPAIR_IF_POSSIBLE = 0
  NO_REPAIR          = 1

class ObjSense(enum.IntEnum):
  MINIMIZE = 1
  MAXIMIZE = -1

class ParameterType(enum.IntEnum):
  NOTDEFINED = 0
  INT        = 1
  INT64      = 2
  DOUBLE     = 3
  STRING     = 4

class QConvexity(enum.IntEnum):
  UNKNOWN         = -1
  NONCONVEX       = 0
  CONVEX          = 1
  REPAIRABLE      = 2
  CONVEXCONE      = 3
  CONECONVERTABLE = 4

class SolInfo(enum.IntEnum):
  ABSPRIMALINFEAS  = 0
  RELPRIMALINFEAS  = 1
  ABSDUALINFEAS    = 2
  RELDUALINFEAS    = 3
  MAXMIPFRACTIONAL = 4
  ABSMIPINFEAS     = 5
  RELMIPINFEAS     = 6

class TunerMode(enum.IntEnum):
  AUTOMATIC = -1
  OFF       = 0
  ON        = 1

class TunerMethod(enum.IntEnum):
  AUTOMATIC        = -1
  LPQUICK          = 0
  MIPQUICK         = 1
  MIPCOMPREHENSIVE = 2
  MIPROOTFOCUS     = 3
  MIPTREEFOCUS     = 4
  MIPSIMPLE        = 5
  SLPQUICK         = 6
  MISLPQUICK       = 7
  MIPHEURISTICS    = 8
  GLOBALQUICK      = 9
  LPNUMERICS       = 10

class TunerTarget(enum.IntEnum):
  AUTOMATIC      = -1
  TIMEGAP        = 0
  TIMEBOUND      = 1
  TIMEOBJVAL     = 2
  INTEGRAL       = 3
  SLPTIME        = 4
  SLPOBJVAL      = 5
  SLPVALIDATION  = 6
  GAP            = 7
  BOUND          = 8
  OBJVAL         = 9
  PRIMALINTEGRAL = 10

class TunerHistory(enum.IntEnum):
  IGNORE = 0
  APPEND = 1
  REUSE  = 2

class TunerRootAlg(enum.IntEnum):
  DUAL    = 1
  PRIMAL  = 2
  BARRIER = 4
  NETWORK = 8

class LPFlags(enum.IntEnum):
  DUAL    = 1
  PRIMAL  = 2
  BARRIER = 4
  NETWORK = 8

class GenConsType(enum.IntEnum):
  MAX = 0
  MIN = 1
  AND = 2
  OR  = 3
  ABS = 4

class Clamping(enum.IntEnum):
  PRIMAL = 1
  DUAL   = 2
  SLACKS = 4
  RDJ    = 8

class RowFlag(enum.IntEnum):
  QUADRATIC = 1
  DELAYED   = 2
  MODELCUT  = 4
  INDICATOR = 8
  NONLINEAR = 16

class ObjControl(enum.IntEnum):
  PRIORITY = 20001
  WEIGHT   = 20002
  ABSTOL   = 20003
  RELTOL   = 20004
  RHS      = 20005

class AllowCompute(enum.IntEnum):
  ALWAYS  = 1
  NEVER   = 0
  DEFAULT = -1

class ComputeLog(enum.IntEnum):
  NEVER        = 0
  REALTIME     = 1
  ONCOMPLETION = 2
  ONERROR      = 3

class Namespaces(enum.IntEnum):
  ROW                = 1
  COLUMN             = 2
  SET                = 3
  PWLCONS            = 4
  GENCONS            = 5
  OBJECTIVE          = 6
  USERFUNC           = 7
  INTERNALFUNC       = 8
  USERFUNCNOCASE     = 9
  INTERNALFUNCNOCASE = 10

class Globalboundingbox(enum.IntEnum):
  NOT_APPLIED = 0
  ORIGINAL    = 1
  AUXILIARY   = 2

class MultiObjOps(enum.IntEnum):
  ENABLED  = 1
  PRESOLVE = 2
  RCFIXING = 4

class IISOps(enum.IntEnum):
  BINARY         = 1
  ZEROLOWER      = 2
  FIXEDVAR       = 4
  BOUND          = 8
  GENINTEGRALITY = 16
  INTEGRALITY    = 17
  VARIABLE       = 25
  EQUALITY       = 32
  GENERAL        = 64
  PWL            = 128
  SET            = 256
  INDICATOR      = 512
  DELAYED        = 1024
  CONSTRAINT     = 2048

class UserSolStatus(enum.IntEnum):
  NOT_CHECKED               = 0
  ACCEPTED_FEASIBLE         = 1
  ACCEPTED_OPTIMIZED        = 2
  SEARCHED_SOL              = 3
  SEARCHED_NOSOL            = 4
  REJECTED_INFEAS_NOSEARCH  = 5
  REJECTED_PARTIAL_NOSEARCH = 6
  REJECTED_FAILED_OPTIMIZE  = 7
  DROPPED                   = 8
  REJECTED_CUTOFF           = 9

class GlobalLSHEURStrategy(enum.IntEnum):
  DEFAULT      = -1
  NONE         = 0
  CONSERVATIVE = 1
  MODERATE     = 2
  AGGRESSIVE   = 3

class BARHGOps(enum.IntEnum):
  ASYM_AVG       = 1
  START_L1       = 2
  START_L2       = 4
  START_LINF     = 8
  OMEGA_CONTRACT = 32
  OMEGA_INF      = 64
  MAX_OBJSCALE   = 128
  NO_OBJSCALE    = 256
  HPDHG          = 512
  HBASE          = 1024

class BasisStatus(enum.IntEnum):
  NONBASIC_LOWER = 0
  BASIC          = 1
  NONBASIC_UPPER = 2
  SUPERBASIC     = 3

del enum
