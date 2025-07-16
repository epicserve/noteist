package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

// Constants for API configuration
const (
	apiBaseURL = "https://api.todoist.com/api/v1"
)

// TodoistClient handles API interactions with Todoist
type TodoistClient struct {
	apiToken string
	client   *http.Client
}

// Project represents a Todoist project
type Project struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

// Task represents a completed Todoist task
type Task struct {
	ID          string    `json:"id"`
	Content     string    `json:"content"`
	Description string    `json:"description"`
	CompletedAt string    `json:"completed_at"`
	ParentID    *string   `json:"parent_id"`
}

// NewTodoistClient creates a new Todoist client
func NewTodoistClient(apiToken string) *TodoistClient {
	return &TodoistClient{
		apiToken: apiToken,
		client:   &http.Client{},
	}
}

// request makes a generic API request
func (c *TodoistClient) request(method, endpoint string, params map[string]string) ([]byte, error) {
	url := fmt.Sprintf("%s/%s", apiBaseURL, endpoint)
	req, err := http.NewRequest(method, url, nil)
	if err != nil {
		return nil, fmt.Errorf("creating request: %w", err)
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.apiToken))
	req.Header.Set("Content-Type", "application/json")

	if len(params) > 0 {
		q := req.URL.Query()
		for k, v := range params {
			q.Add(k, v)
		}
		req.URL.RawQuery = q.Encode()
	}

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("making request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API returned status code %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("reading response: %w", err)
	}

	return body, nil
}

// GetProjects fetches all projects
func (c *TodoistClient) GetProjects() ([]Project, error) {
	body, err := c.request("GET", "projects", nil)
	if err != nil {
		return nil, err
	}

	var projects struct {
		Results []Project `json:"results"`
	}
	if err := json.Unmarshal(body, &projects); err != nil {
		return nil, fmt.Errorf("unmarshaling projects: %w", err)
	}

	return projects.Results, nil
}

// FindProjectByName finds a project by name (case-insensitive)
func (c *TodoistClient) FindProjectByName(name string) (*Project, error) {
	projects, err := c.GetProjects()
	if err != nil {
		return nil, err
	}

	for _, project := range projects {
		if strings.EqualFold(project.Name, name) {
			fmt.Printf("Found project: %s (ID: %s)\n", project.Name, project.ID)
			return &project, nil
		}
	}
	return nil, nil
}

// GetCompletedTasks fetches completed tasks for a project since a given date
func (c *TodoistClient) GetCompletedTasks(projectID string, since time.Time) ([]Task, error) {
	params := map[string]string{
		"project_id": projectID,
		"since":      since.Format("2006-01-02T15:04:05Z"),
		"until":      time.Now().Format("2006-01-02T15:04:05Z"),
	}

	body, err := c.request("GET", "tasks/completed/by_completion_date", params)
	if err != nil {
		return nil, err
	}

	var result struct {
		Items []Task `json:"items"`
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("unmarshaling tasks: %w", err)
	}

	return result.Items, nil
}

// formatTask formats a task for display
func formatTask(prevTask, task Task) string {
	completedAt, _ := time.Parse(time.RFC3339, task.CompletedAt)
	completedLocal := completedAt.Format("2006-01-02 15:04:05")

	bullet := "* "
	if task.ParentID != nil {
		bullet = "  - "
	}
	result := fmt.Sprintf("%s%s (completed: %s)", bullet, task.Content, completedLocal)

	if prevTask.ParentID != nil && task.ParentID == nil {
		result = fmt.Sprintf("\n%s", result)
	}
	if task.Description != "" {
		result += fmt.Sprintf("\n%s%s\n", strings.Repeat(" ", len(bullet)), task.Description)
	}

	return result
}

func main() {
	// Load API token from environment
	apiToken := os.Getenv("TODOIST_API_TOKEN")
	if apiToken == "" {
		fmt.Println("Error: TODOIST_API_TOKEN environment variable is not set")
		os.Exit(1)
	}

	// Initialize client
	client := NewTodoistClient(apiToken)

	// Find project
	project, err := client.FindProjectByName("Canopy")
	if err != nil {
		fmt.Printf("Error fetching projects: %v\n", err)
		os.Exit(1)
	}
	if project == nil {
		fmt.Println("Error: Could not find project named 'Canopy'")
		projects, err := client.GetProjects()
		if err != nil {
			fmt.Printf("Error fetching projects: %v\n", err)
			os.Exit(1)
		}
		fmt.Println("Available projects:")
		for _, p := range projects {
			fmt.Printf("  - %s\n", p.Name)
		}
		os.Exit(1)
	}

	// Get completed tasks from the last week
	oneWeekAgo := time.Now().AddDate(0, 0, -7)
	tasks, err := client.GetCompletedTasks(project.ID, oneWeekAgo)
	if err != nil {
		fmt.Printf("Error fetching completed tasks: %v\n", err)
		os.Exit(1)
	}

	// Display results
	if len(tasks) == 0 {
		fmt.Println("No completed tasks found in the last week.")
		return
	}

	fmt.Printf("\n📋 Completed Tasks in #Canopy (%s to %s)\n",
		oneWeekAgo.Format("2006-01-02"), time.Now().Format("2006-01-02"))
	fmt.Println(strings.Repeat("=", 56))
	fmt.Printf("Total completed: %d\n\n", len(tasks))

	// Format and print tasks
	var prevTask Task
	for _, task := range tasks {
		fmt.Println(formatTask(prevTask, task))
		prevTask = task
	}
}