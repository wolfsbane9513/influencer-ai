# enhanced_contract_e2e_test.py - ENHANCED CONTRACT AUTOMATION
import requests
import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class EnhancedContractE2ETest:
    """
    🎯 ENHANCED CONTRACT END-TO-END AUTOMATION
    
    Complete automation for enhanced contract workflow:
    1. System health verification
    2. Enhanced contract generation with multiple scenarios
    3. Contract validation and verification
    4. Automatic file generation and storage
    5. Comprehensive reporting
    6. Error handling and recovery
    """
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.test_results = {}
        self.generated_contracts = []
        self.test_scenarios = []
        
        print("🎯 ENHANCED CONTRACT - FULL AUTOMATION SUITE")
        print("=" * 70)
        print("Automated enhanced contract generation, validation, and verification")
        print()
    
    def run_complete_automation(self):
        """Run the complete enhanced contract automation suite"""
        
        # Phase 1: System Verification
        print("📋 PHASE 1: SYSTEM VERIFICATION")
        print("-" * 50)
        
        if not self.test_system_health():
            print("❌ System health check failed - aborting automation")
            return False
        
        if not self.verify_enhanced_contract_endpoint():
            print("❌ Enhanced contract endpoint verification failed - aborting")
            return False
        
        # Phase 2: Enhanced Contract Generation (Multiple Scenarios)
        print("\n📋 PHASE 2: ENHANCED CONTRACT GENERATION")
        print("-" * 50)
        
        self.generate_contracts_all_scenarios()
        
        # Phase 3: Contract Validation & Verification
        print("\n📋 PHASE 3: CONTRACT VALIDATION & VERIFICATION")
        print("-" * 50)
        
        self.validate_all_generated_contracts()
        
        # Phase 4: File Generation & Storage
        print("\n📋 PHASE 4: FILE GENERATION & STORAGE")
        print("-" * 50)
        
        self.save_contracts_to_files()
        
        # Phase 5: Comprehensive Reporting
        print("\n📋 PHASE 5: COMPREHENSIVE REPORTING")
        print("-" * 50)
        
        self.generate_comprehensive_report()
        
        print("\n🎉 ENHANCED CONTRACT AUTOMATION COMPLETED!")
        print("=" * 70)
        
        return True
    
    def test_system_health(self):
        """Test system health and connectivity"""
        
        try:
            print("1. 🏥 Testing system health...")
            
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ System Status: {health_data.get('status', 'unknown')}")
                print(f"   📊 Services Active: {len(health_data.get('services', {}))}")
                
                self.test_results['system_health'] = {
                    'status': 'passed',
                    'response_time': response.elapsed.total_seconds(),
                    'services': health_data.get('services', {})
                }
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                self.test_results['system_health'] = {'status': 'failed', 'error': response.status_code}
                return False
                
        except Exception as e:
            print(f"   ❌ Health check exception: {e}")
            self.test_results['system_health'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def verify_enhanced_contract_endpoint(self):
        """Verify enhanced contract endpoint is accessible"""
        
        try:
            print("2. 📝 Verifying enhanced contract endpoint...")
            
            # Test with minimal data to verify endpoint accessibility
            test_data = {
                "creator_name": "EndpointTestCreator",
                "compensation": 100.0,
                "campaign_details": {"test": "endpoint_verification"}
            }
            
            response = requests.post(
                f"{self.base_url}/api/webhook/generate-enhanced-contract",
                json=test_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Endpoint Status: {data.get('status', 'unknown')}")
                print(f"   📋 Contract Generated: {data.get('contract_generated', False)}")
                
                self.test_results['endpoint_verification'] = {
                    'status': 'passed',
                    'contract_generated': data.get('contract_generated', False),
                    'response_time': response.elapsed.total_seconds()
                }
                return True
            else:
                print(f"   ❌ Endpoint verification failed: {response.status_code}")
                self.test_results['endpoint_verification'] = {'status': 'failed', 'error': response.status_code}
                return False
                
        except Exception as e:
            print(f"   ❌ Endpoint verification exception: {e}")
            self.test_results['endpoint_verification'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def generate_contracts_all_scenarios(self):
        """Generate enhanced contracts for multiple test scenarios"""
        
        # Define comprehensive test scenarios
        self.test_scenarios = [
            {
                "name": "High-Value Tech Influencer",
                "creator_name": "TechGuru_Alex",
                "compensation": 5000.0,
                "campaign_details": {
                    "brand": "TechCorp Industries",
                    "product": "AI-Powered Smart Device Pro",
                    "category": "Technology",
                    "audience_size": "500K+",
                    "engagement_rate": "8.5%"
                }
            },
            {
                "name": "Fashion Micro-Influencer",
                "creator_name": "StyleQueen_Maya",
                "compensation": 1500.0,
                "campaign_details": {
                    "brand": "Elegant Fashion House",
                    "product": "Premium Designer Collection",
                    "category": "Fashion & Lifestyle",
                    "audience_size": "150K",
                    "engagement_rate": "12.3%"
                }
            },
            {
                "name": "Fitness Content Creator",
                "creator_name": "FitLife_Marcus",
                "compensation": 3000.0,
                "campaign_details": {
                    "brand": "HealthFirst Supplements",
                    "product": "Elite Performance Protein Series",
                    "category": "Health & Fitness",
                    "audience_size": "300K",
                    "engagement_rate": "9.7%"
                }
            },
            {
                "name": "Gaming Streamer",
                "creator_name": "GameMaster_Zoe",
                "compensation": 4500.0,
                "campaign_details": {
                    "brand": "GameZone Technologies",
                    "product": "Ultra Gaming Headset V2",
                    "category": "Gaming & Entertainment",
                    "audience_size": "750K",
                    "engagement_rate": "15.2%"
                }
            },
            {
                "name": "Beauty Content Creator",
                "creator_name": "GlowUp_Sophia",
                "compensation": 2500.0,
                "campaign_details": {
                    "brand": "LuxBeauty Cosmetics",
                    "product": "Radiant Skin Care Bundle",
                    "category": "Beauty & Skincare",
                    "audience_size": "400K",
                    "engagement_rate": "11.8%"
                }
            }
        ]
        
        print(f"3. 📝 Generating enhanced contracts for {len(self.test_scenarios)} scenarios...")
        
        successful_generations = 0
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            try:
                print(f"\n   🎯 Scenario {i}: {scenario['name']}")
                print(f"      Creator: {scenario['creator_name']}")
                print(f"      Compensation: ${scenario['compensation']:,.2f}")
                
                response = requests.post(
                    f"{self.base_url}/api/webhook/generate-enhanced-contract",
                    json=scenario,
                    timeout=20
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('status') == 'success' and data.get('contract_generated'):
                        print(f"      ✅ Contract generated successfully")
                        print(f"      📋 Contract ID: {data.get('contract_metadata', {}).get('contract_id', 'N/A')}")
                        
                        # Store contract data
                        contract_info = {
                            'scenario': scenario,
                            'response_data': data,
                            'generation_time': datetime.now().isoformat(),
                            'contract_id': data.get('contract_metadata', {}).get('contract_id'),
                            'full_contract': data.get('full_contract', '')
                        }
                        
                        self.generated_contracts.append(contract_info)
                        successful_generations += 1
                        
                        # Brief pause between generations
                        time.sleep(1)
                        
                    else:
                        print(f"      ❌ Contract generation failed: {data.get('message', 'Unknown error')}")
                        
                else:
                    print(f"      ❌ Request failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Exception during generation: {e}")
        
        print(f"\n📊 Contract Generation Summary:")
        print(f"   ✅ Successful: {successful_generations}/{len(self.test_scenarios)}")
        print(f"   📝 Total Contracts Generated: {len(self.generated_contracts)}")
        
        self.test_results['contract_generation'] = {
            'total_scenarios': len(self.test_scenarios),
            'successful_generations': successful_generations,
            'generated_contracts': len(self.generated_contracts),
            'success_rate': f"{(successful_generations/len(self.test_scenarios)*100):.1f}%"
        }
    
    def validate_all_generated_contracts(self):
        """Validate all generated contracts for completeness and accuracy"""
        
        print("4. ✅ Validating all generated contracts...")
        
        validation_results = []
        
        for i, contract in enumerate(self.generated_contracts, 1):
            try:
                print(f"\n   📋 Validating Contract {i}: {contract['scenario']['creator_name']}")
                
                validation = self.validate_single_contract(contract)
                validation_results.append(validation)
                
                if validation['is_valid']:
                    print(f"      ✅ Validation passed - Score: {validation['validation_score']:.1f}%")
                else:
                    print(f"      ❌ Validation failed - Issues: {len(validation['issues'])}")
                    for issue in validation['issues'][:3]:  # Show first 3 issues
                        print(f"         • {issue}")
                
            except Exception as e:
                print(f"      ❌ Validation exception: {e}")
                validation_results.append({'is_valid': False, 'error': str(e)})
        
        # Calculate validation summary
        valid_contracts = sum(1 for v in validation_results if v.get('is_valid', False))
        avg_score = sum(v.get('validation_score', 0) for v in validation_results) / len(validation_results) if validation_results else 0
        
        print(f"\n📊 Validation Summary:")
        print(f"   ✅ Valid Contracts: {valid_contracts}/{len(self.generated_contracts)}")
        print(f"   📈 Average Validation Score: {avg_score:.1f}%")
        
        self.test_results['validation'] = {
            'total_validated': len(validation_results),
            'valid_contracts': valid_contracts,
            'validation_rate': f"{(valid_contracts/len(validation_results)*100):.1f}%" if validation_results else "0%",
            'average_score': f"{avg_score:.1f}%",
            'detailed_results': validation_results
        }
    
    def validate_single_contract(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single contract for completeness and accuracy"""
        
        issues = []
        score = 100
        
        contract_text = contract.get('full_contract', '')
        scenario = contract.get('scenario', {})
        response_data = contract.get('response_data', {})
        
        # Check contract text completeness
        if not contract_text or len(contract_text.strip()) < 100:
            issues.append("Contract text is too short or missing")
            score -= 20
        
        # Check if creator name is included
        creator_name = scenario.get('creator_name', '')
        if creator_name and creator_name not in contract_text:
            issues.append("Creator name not found in contract text")
            score -= 15
        
        # Check compensation amount
        compensation = scenario.get('compensation', 0)
        if compensation > 0 and str(compensation) not in contract_text:
            issues.append("Compensation amount not clearly stated in contract")
            score -= 15
        
        # Check brand/product information
        campaign_details = scenario.get('campaign_details', {})
        brand = campaign_details.get('brand', '')
        product = campaign_details.get('product', '')
        
        if brand and brand not in contract_text:
            issues.append("Brand name not found in contract")
            score -= 10
        
        if product and product not in contract_text:
            issues.append("Product name not found in contract")
            score -= 10
        
        # Check response data completeness
        if not response_data.get('status') == 'success':
            issues.append("Response status indicates failure")
            score -= 20
        
        if not response_data.get('contract_generated'):
            issues.append("Contract generation flag is false")
            score -= 20
        
        # Check for required contract elements
        required_elements = ['TERMS', 'Creator:', 'Brand:', 'Compensation:', 'Generated:']
        for element in required_elements:
            if element not in contract_text:
                issues.append(f"Missing required element: {element}")
                score -= 5
        
        return {
            'is_valid': len(issues) == 0,
            'validation_score': max(0, score),
            'issues': issues,
            'contract_length': len(contract_text),
            'has_creator_name': creator_name in contract_text,
            'has_compensation': str(compensation) in contract_text,
            'has_brand_info': brand in contract_text,
            'has_product_info': product in contract_text
        }
    
    def save_contracts_to_files(self):
        """Save all generated contracts to individual files"""
        
        print("5. 💾 Saving contracts to files...")
        
        saved_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, contract in enumerate(self.generated_contracts, 1):
            try:
                creator_name = contract['scenario']['creator_name']
                contract_id = contract.get('contract_id', f'contract_{i}')
                
                # Create filename
                filename = f"enhanced_contract_{creator_name}_{timestamp}.txt"
                
                # Prepare contract content with metadata
                contract_content = f"""# ENHANCED CONTRACT - AUTOMATED GENERATION
# Generated: {contract['generation_time']}
# Creator: {creator_name}
# Contract ID: {contract_id}
# Scenario: {contract['scenario']['name']}
# ================================================

{contract['full_contract']}

# ================================================
# GENERATION METADATA
# ================================================
# Compensation: ${contract['scenario']['compensation']:,.2f}
# Brand: {contract['scenario']['campaign_details'].get('brand', 'N/A')}
# Product: {contract['scenario']['campaign_details'].get('product', 'N/A')}
# Category: {contract['scenario']['campaign_details'].get('category', 'N/A')}
# Generation Timestamp: {contract['generation_time']}
# Validation Status: {"PASSED" if contract.get('validation', {}).get('is_valid', False) else "PENDING"}
"""
                
                # Save to file
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(contract_content)
                
                saved_files.append(filename)
                print(f"   ✅ Saved: {filename}")
                
            except Exception as e:
                print(f"   ❌ Failed to save contract {i}: {e}")
        
        print(f"\n📁 File Generation Summary:")
        print(f"   💾 Files Saved: {len(saved_files)}")
        print(f"   📂 Location: Current directory")
        
        self.test_results['file_generation'] = {
            'files_saved': len(saved_files),
            'filenames': saved_files,
            'save_location': 'current_directory'
        }
    
    def generate_comprehensive_report(self):
        """Generate comprehensive automation report"""
        
        print("6. 📊 Generating comprehensive automation report...")
        
        # Calculate overall success metrics
        total_scenarios = len(self.test_scenarios)
        successful_generations = len(self.generated_contracts)
        generation_success_rate = (successful_generations / total_scenarios * 100) if total_scenarios > 0 else 0
        
        # Prepare detailed report
        report = {
            "enhanced_contract_automation_report": {
                "execution_timestamp": datetime.now().isoformat(),
                "automation_summary": {
                    "total_scenarios_tested": total_scenarios,
                    "successful_contract_generations": successful_generations,
                    "generation_success_rate": f"{generation_success_rate:.1f}%",
                    "total_files_saved": len(self.test_results.get('file_generation', {}).get('filenames', [])),
                    "overall_status": "SUCCESS" if generation_success_rate >= 80 else "PARTIAL_SUCCESS" if generation_success_rate >= 50 else "FAILED"
                },
                "phase_results": self.test_results,
                "generated_contracts_summary": [
                    {
                        "scenario_name": contract['scenario']['name'],
                        "creator_name": contract['scenario']['creator_name'],
                        "compensation": contract['scenario']['compensation'],
                        "brand": contract['scenario']['campaign_details'].get('brand'),
                        "product": contract['scenario']['campaign_details'].get('product'),
                        "contract_id": contract.get('contract_id'),
                        "generation_time": contract['generation_time'],
                        "contract_length": len(contract.get('full_contract', ''))
                    }
                    for contract in self.generated_contracts
                ],
                "automation_recommendations": self._generate_recommendations()
            }
        }
        
        # Save report to file
        report_filename = f"enhanced_contract_automation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Report saved: {report_filename}")
            
            # Display summary
            print(f"\n📈 AUTOMATION SUMMARY:")
            print(f"   🎯 Scenarios Tested: {total_scenarios}")
            print(f"   ✅ Successful Generations: {successful_generations}")
            print(f"   📊 Success Rate: {generation_success_rate:.1f}%")
            print(f"   💾 Files Generated: {len(self.test_results.get('file_generation', {}).get('filenames', []))}")
            print(f"   📋 Overall Status: {report['enhanced_contract_automation_report']['automation_summary']['overall_status']}")
            
        except Exception as e:
            print(f"   ❌ Failed to save report: {e}")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate automation recommendations based on results"""
        
        recommendations = []
        
        # Check generation success rate
        total_scenarios = len(self.test_scenarios)
        successful_generations = len(self.generated_contracts)
        success_rate = (successful_generations / total_scenarios * 100) if total_scenarios > 0 else 0
        
        if success_rate < 100:
            recommendations.append("Some contract generations failed - investigate error handling and retry mechanisms")
        
        if success_rate >= 90:
            recommendations.append("Excellent generation success rate - consider adding more complex scenarios")
        
        # Check validation results
        validation_results = self.test_results.get('validation', {})
        validation_rate = float(validation_results.get('validation_rate', '0%').replace('%', ''))
        
        if validation_rate < 90:
            recommendations.append("Contract validation rate could be improved - review contract templates and validation logic")
        
        # Check system performance
        system_health = self.test_results.get('system_health', {})
        if system_health.get('response_time', 0) > 5:
            recommendations.append("System response time is slow - consider performance optimization")
        
        if not recommendations:
            recommendations.append("All automation phases completed successfully - system is performing optimally")
        
        return recommendations


def main():
    """
    🚀 MAIN EXECUTION FUNCTION
    
    Run the complete enhanced contract automation suite
    """
    
    print("🎯 ENHANCED CONTRACT AUTOMATION STARTING...")
    print()
    
    # Initialize and run automation
    automation = EnhancedContractE2ETest()
    
    # Run the complete automation suite
    try:
        success = automation.run_complete_automation()
        
        if success:
            print("\n🎉 ENHANCED CONTRACT AUTOMATION COMPLETED SUCCESSFULLY!")
            print("   📁 Check current directory for generated contracts and reports")
            print("   📊 Review the automation report for detailed results")
        else:
            print("\n❌ ENHANCED CONTRACT AUTOMATION ENCOUNTERED ISSUES")
            print("   📋 Check the error messages above for troubleshooting")
            
    except KeyboardInterrupt:
        print("\n⚠️ Automation interrupted by user")
    except Exception as e:
        print(f"\n❌ Automation failed with exception: {e}")

if __name__ == "__main__":
    main() 