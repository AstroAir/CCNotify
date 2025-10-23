#!/usr/bin/env python3
"""
Test runner for Claude Prompt Tracker System
Provides manual testing capabilities using the test data
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from test_data import TestDataGenerator


class PromptTrackerTestRunner:
    """Test runner for prompt tracker system"""
    
    def __init__(self):
        self.script_path = Path(__file__).parent.parent / "ccnotify.py"
        self.test_data_dir = Path(__file__).parent / "test_data"
        
    def run_single_event(self, event_data, delay=0.5):
        """Run a single event through the prompt tracker"""
        print(f"Running event: {event_data['hook_event_name']} for session {event_data['session_id']}")
        
        try:
            # Convert event data to JSON
            json_input = json.dumps(event_data)
            
            # Run the prompt tracker script
            result = subprocess.run(
                [sys.executable, str(self.script_path)],
                input=json_input,
                text=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✓ Event processed successfully")
                if result.stderr:
                    print(f"  Log: {result.stderr.strip()}")
            else:
                print(f"✗ Event failed with return code {result.returncode}")
                if result.stderr:
                    print(f"  Error: {result.stderr.strip()}")
            
            # Add delay between events
            if delay > 0:
                time.sleep(delay)
                
        except subprocess.TimeoutExpired:
            print("✗ Event timed out")
        except Exception as e:
            print(f"✗ Exception: {e}")
    
    def run_scenario(self, scenario_name, delay=1.0):
        """Run a complete test scenario"""
        print(f"\n{'='*50}")
        print(f"Running Scenario: {scenario_name}")
        print(f"{'='*50}")
        
        scenarios = TestDataGenerator.get_all_scenarios()
        if scenario_name not in scenarios:
            print(f"Unknown scenario: {scenario_name}")
            return
        
        events = scenarios[scenario_name]
        
        for i, event in enumerate(events, 1):
            print(f"\n[{i}/{len(events)}] ", end="")
            self.run_single_event(event, delay)
        
        print(f"\n✓ Scenario {scenario_name} completed!")
    
    def run_all_scenarios(self, delay=1.0):
        """Run all test scenarios"""
        scenarios = TestDataGenerator.get_all_scenarios()
        
        print("Starting comprehensive test run...")
        print(f"Total scenarios: {len(scenarios)}")
        
        for scenario_name in scenarios.keys():
            self.run_scenario(scenario_name, delay)
            
            # Longer delay between scenarios
            if delay > 0:
                print(f"\nWaiting {delay*2} seconds before next scenario...")
                time.sleep(delay * 2)
        
        print("\n🎉 All scenarios completed!")
    
    def verify_database(self):
        """Verify database contents after testing"""
        import sqlite3
        from pathlib import Path

        db_path = Path.home() / ".claude" / "ccnotify" / "ccnotify.db"

        if not db_path.exists():
            print("Database file not found!")
            return
        
        print(f"\n{'='*50}")
        print("Database Verification")
        print(f"{'='*50}")
        
        with sqlite3.connect(db_path) as conn:
            # Count total records
            cursor = conn.execute("SELECT COUNT(*) FROM prompt")
            total_records = cursor.fetchone()[0]
            print(f"Total records: {total_records}")
            
            # Count by session
            cursor = conn.execute("""
                SELECT session_id, COUNT(*), MAX(seq)
                FROM prompt
                GROUP BY session_id
                ORDER BY session_id
            """)
            
            print("\nRecords by session:")
            for row in cursor.fetchall():
                session_id, count, max_seq = row
                print(f"  {session_id}: {count} records, max seq: {max_seq}")
            
            # Show completed vs incomplete
            cursor = conn.execute("""
                SELECT 
                    COUNT(CASE WHEN stoped_at IS NOT NULL THEN 1 END) as completed,
                    COUNT(CASE WHEN stoped_at IS NULL THEN 1 END) as incomplete
                FROM prompt
            """)
            
            completed, incomplete = cursor.fetchone()
            print(f"\nTask status:")
            print(f"  Completed: {completed}")
            print(f"  Incomplete: {incomplete}")
            
            # Show recent records
            cursor = conn.execute("""
                SELECT session_id, dirname, prompt, seq, 
                       created_at, stoped_at, lastWaitUserAt
                FROM prompt
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            print(f"\nRecent records:")
            for row in cursor.fetchall():
                session_id, dirname, prompt, seq, created_at, stoped_at, wait_at = row
                prompt_short = prompt[:30] + "..." if prompt and len(prompt) > 30 else prompt
                status = "✓" if stoped_at else "⏳"
                wait_status = "⌛" if wait_at else ""
                print(f"  {status} {session_id}[{seq}] {dirname}: {prompt_short} {wait_status}")
    
    def interactive_mode(self):
        """Interactive testing mode"""
        scenarios = TestDataGenerator.get_all_scenarios()
        
        while True:
            print(f"\n{'='*40}")
            print("Interactive Test Mode")
            print(f"{'='*40}")
            print("Available scenarios:")
            
            scenario_list = list(scenarios.keys())
            for i, scenario in enumerate(scenario_list, 1):
                print(f"  {i}. {scenario}")
            
            print("\nOptions:")
            print("  a. Run all scenarios")
            print("  v. Verify database")
            print("  q. Quit")
            
            choice = input("\nSelect option: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 'a':
                delay = input("Enter delay between events (default 1.0s): ").strip()
                delay = float(delay) if delay else 1.0
                self.run_all_scenarios(delay)
            elif choice == 'v':
                self.verify_database()
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(scenario_list):
                    delay = input("Enter delay between events (default 1.0s): ").strip()
                    delay = float(delay) if delay else 1.0
                    self.run_scenario(scenario_list[idx], delay)
                else:
                    print("Invalid scenario number!")
            else:
                print("Invalid choice!")


def main():
    """Main entry point"""
    runner = PromptTrackerTestRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "all":
            delay = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
            runner.run_all_scenarios(delay)
        elif command == "verify":
            runner.verify_database()
        elif command.startswith("scenario_"):
            delay = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
            runner.run_scenario(command, delay)
        else:
            print("Usage:")
            print("  python run_tests.py                    # Interactive mode")
            print("  python run_tests.py all [delay]        # Run all scenarios")
            print("  python run_tests.py scenario_1 [delay] # Run specific scenario")
            print("  python run_tests.py verify             # Verify database")
    else:
        runner.interactive_mode()


if __name__ == "__main__":
    main()