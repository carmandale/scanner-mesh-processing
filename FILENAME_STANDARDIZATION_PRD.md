# Scanner Pipeline Filename Standardization PRD

**Version:** 1.0  
**Date:** July 2025  
**Author:** Dale Carman  
**Status:** Draft - Pending Review

---

## 1. Executive Summary

This PRD outlines the standardization of file naming conventions across the Scanner Mesh Processing Pipeline. The initiative aims to remove version numbers from filenames and adopt consistent snake_case naming following Python PEP 8 standards.

### 1.1 Objectives
- Remove "_vXX" versioning convention from all pipeline files
- Standardize naming to snake_case following PEP 8 best practices
- Improve code maintainability and readability
- Reduce confusion around "current" vs "legacy" versions

### 1.2 Success Criteria
- All pipeline scripts follow consistent snake_case naming
- Zero version numbers in active pipeline filenames
- All references updated across configuration, documentation, and scripts
- Pipeline functionality remains unchanged after migration

---

## 2. Current State Analysis

### 2.1 Naming Inconsistencies

**Current Mixed Conventions:**
```
Snake_case (✅ Correct):
- face_detector_v3.py
- rotate_mesh.py

PascalCase (❌ Non-standard):
- CleanUp_v5.py
- AddRig.v05.py

camelCase (❌ Non-standard):
- poseTest_v2.py
- generateMesh_v3.sh
- grooveMeshCheck_v3.py
- prepUSDZ_v4.py
```

### 2.2 Version Number Issues

**Problems with Current Versioning:**
- Unclear which version is "current" without inspecting pipeline
- Version numbers embedded in critical path references
- Legacy versions accumulating in repository
- Import statements tied to specific versions

---

## 3. Proposed Changes

### 3.1 File Renaming Matrix

| Current Name | New Name | Type | Impact |
|--------------|----------|------|---------|
| `generateMesh_v3.sh` | `generate_mesh.sh` | Script | Medium |
| `grooveMeshCheck_v3.py` | `groove_mesh_check.py` | Python | Medium |
| `prepUSDZ_v4.py` | `prep_usdz.py` | Python | Low |
| `CleanUp_v5.py` | `cleanup.py` | Python | High |
| `AddRig.v05.py` | `add_rig.py` | Python | High |
| `poseTest_v2.py` | `pose_test.py` | Python | Medium |
| `face_detector_v3.py` | `face_detector.py` | Python | Medium |
| `skeleton_template_v05.blend` | `skeleton_template.blend` | Asset | Medium |
| `pose_test_render_v01.blend` | `pose_test_render.blend` | Asset | Low |
| `pose_test_rig_v01.blend` | `pose_test_rig.blend` | Asset | Low |

### 3.2 Naming Convention Standard

**Adopted Standard: snake_case (PEP 8)**
- All lowercase letters
- Words separated by underscores
- Descriptive and readable
- Consistent with Python ecosystem

**Examples:**
```python
# Good
face_detector.py
generate_mesh.sh
cleanup.py

# Bad
FaceDetector.py
GenerateMesh.sh
CleanUp.py
```

---

## 4. Implementation Plan

### 4.1 Phase 1: File Creation and Internal Updates
**Duration:** 2-3 hours  
**Risk Level:** Low

**Tasks:**
1. Create renamed copies of all current files
2. Update internal script references (imports, function calls)
3. Update hardcoded paths within scripts
4. Verify script functionality with new names

**Files to Update:**
- `grooveMeshCheck_v3.py` → Update `import prepUSDZ_v3` to `import prep_usdz`
- `generateMesh_v3.sh` → Update script path references
- All Python scripts → Update any internal version references

### 4.2 Phase 2: Pipeline Integration
**Duration:** 1-2 hours  
**Risk Level:** Medium

**Tasks:**
1. Update `runScriptAutomated.sh` with new script names
2. Update `generateMesh.sh` (formerly v3) script references
3. Update configuration files
4. Test full pipeline execution

**Critical Files:**
- `runScriptAutomated.sh` (Lines 627, 655, 722, 752, 781)
- `config.json`
- `INSTALL.sh`

### 4.3 Phase 3: Documentation and Configuration
**Duration:** 1 hour  
**Risk Level:** Low

**Tasks:**
1. Update all documentation files
2. Update installation scripts
3. Update configuration management
4. Update help text and error messages

**Files to Update:**
- `README.md`
- `AUDIT_REPORT.md`
- `CONFIG_SYSTEM.md`
- `INSTALL.sh`

### 4.4 Phase 4: Legacy Cleanup
**Duration:** 30 minutes  
**Risk Level:** Low

**Tasks:**
1. Move old versioned files to `_ARCHIVE/`
2. Verify no remaining references
3. Update `.gitignore` if needed
4. Clean up any temporary files

---

## 5. Technical Requirements

### 5.1 Backward Compatibility
- **Not Required:** This is an internal refactoring
- **Migration Path:** Direct replacement, no compatibility layer needed
- **External Dependencies:** None affected

### 5.2 Testing Requirements
- Full pipeline execution test with sample scan
- Verify all 5 steps complete successfully
- Compare output quality before/after changes
- Test error handling and logging

### 5.3 Rollback Plan
- Keep versioned files in `_ARCHIVE/` during initial deployment
- Document rollback procedure
- Test rollback process before final cleanup

---

## 6. Impact Assessment

### 6.1 High Impact Files
**Scripts that are central to pipeline:**
- `cleanup.py` (formerly CleanUp_v5.py) - Core mesh processing
- `add_rig.py` (formerly AddRig.v05.py) - Rigging system
- `runScriptAutomated.sh` - Pipeline orchestrator

### 6.2 Medium Impact Files
**Scripts with multiple dependencies:**
- `generate_mesh.sh` - References other scripts
- `groove_mesh_check.py` - Imports other modules
- `face_detector.py` - Called by pipeline

### 6.3 Low Impact Files
**Standalone or utility scripts:**
- `prep_usdz.py` - Utility function
- Template `.blend` files - Asset references

---

## 7. Risk Analysis

### 7.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| Import statement failures | Medium | High | Thorough testing of all imports |
| Pipeline execution failures | Low | High | Comprehensive end-to-end testing |
| Configuration errors | Medium | Medium | Validate all config files |
| Documentation inconsistencies | High | Low | Systematic doc review |

### 7.2 Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| User confusion during transition | Medium | Low | Clear communication plan |
| Legacy script execution | Low | Medium | Archive old versions safely |
| Deployment issues | Low | High | Test deployment process |

---

## 8. Testing Strategy

### 8.1 Unit Testing
- Test each renamed script independently
- Verify imports and dependencies resolve correctly
- Test command-line argument parsing

### 8.2 Integration Testing
- Run complete pipeline with sample data
- Verify all 5 steps execute in sequence
- Test error handling and logging

### 8.3 Regression Testing
- Compare outputs before/after changes
- Verify performance metrics unchanged
- Test edge cases and error conditions

### 8.4 User Acceptance Testing
- Verify documentation accuracy
- Test installation process
- Validate help text and error messages

---

## 9. Success Metrics

### 9.1 Functional Metrics
- ✅ 100% of pipeline scripts follow snake_case naming
- ✅ 0 version numbers in active pipeline files
- ✅ All tests pass after migration
- ✅ Pipeline execution time unchanged

### 9.2 Quality Metrics
- ✅ All documentation updated and consistent
- ✅ No broken references or imports
- ✅ Clean separation of active vs archived files
- ✅ Installation process works correctly

---

## 10. Dependencies and Constraints

### 10.1 Dependencies
- Access to development environment
- Ability to test full pipeline execution
- Sample scan data for testing

### 10.2 Constraints
- Must maintain pipeline functionality
- Cannot break existing workflows
- Must preserve output quality

---

## 11. Timeline and Milestones

### 11.1 Estimated Timeline
**Total Duration:** 4-6 hours

```
Phase 1: File Creation and Internal Updates    [2-3 hours]
Phase 2: Pipeline Integration                  [1-2 hours]
Phase 3: Documentation and Configuration       [1 hour]
Phase 4: Legacy Cleanup                        [30 minutes]
```

### 11.2 Milestones
- **M1:** All files renamed and internally consistent
- **M2:** Pipeline executes successfully with new names
- **M3:** Documentation and configuration updated
- **M4:** Legacy cleanup completed

---

## 12. Approval and Next Steps

### 12.1 Required Approvals
- [ ] Technical review and approval
- [ ] Testing plan approval
- [ ] Implementation timeline approval

### 12.2 Next Steps
1. **Review this PRD** - Stakeholder feedback and approval
2. **Execute Phase 1** - Create renamed files and update internals
3. **Testing** - Comprehensive pipeline testing
4. **Deployment** - Roll out changes systematically
5. **Documentation** - Update all references and guides

---

## 13. Appendix

### 13.1 Complete File Mapping
```bash
# Scripts
generateMesh_v3.sh              → generate_mesh.sh
grooveMeshCheck_v3.py           → groove_mesh_check.py
prepUSDZ_v4.py                  → prep_usdz.py
prepUSDZ_v3.py                  → move to _ARCHIVE
CleanUp_v5.py                   → cleanup.py
AddRig.v05.py                   → add_rig.py
poseTest_v2.py                  → pose_test.py
face_detector_v3.py             → face_detector.py

# Templates
skeleton_template_v05.blend     → skeleton_template.blend
pose_test_render_v01.blend      → pose_test_render.blend
pose_test_rig_v01.blend         → pose_test_rig.blend
```

### 13.2 Reference Files to Update
```bash
# Core pipeline
runScriptAutomated.sh           # Multiple script references
config.json                     # Configuration paths
INSTALL.sh                      # Installation script

# Documentation
README.md                       # Usage examples
AUDIT_REPORT.md                 # System documentation
CONFIG_SYSTEM.md                # Configuration guide
```

---

**Document Status:** Ready for Review  
**Next Review Date:** Upon stakeholder feedback  
**Implementation Target:** TBD based on approval 