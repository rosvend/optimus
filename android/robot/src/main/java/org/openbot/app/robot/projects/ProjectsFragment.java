package org.openbot.app.robot.projects;

import android.os.Bundle;
import android.util.SparseArray;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.fragment.app.Fragment;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.GridLayoutManager;
import com.google.android.material.bottomsheet.BottomSheetBehavior;
import java.util.ArrayList;
import org.openbot.app.robot.R;
import org.openbot.app.robot.databinding.FragmentProjectsBinding;
import org.openbot.app.robot.env.SharedPreferencesManager;
import org.openbot.app.robot.main.CommonRecyclerViewAdapter;
import org.openbot.app.robot.utils.BotFunctionUtils;

/**
 * Shows the locally stored playground projects. Tapping one asks for confirmation and hands its
 * JavaScript to {@link BlocklyExecutingFragment} through its static {@code finalCode} holder.
 */
public class ProjectsFragment extends Fragment {
  private FragmentProjectsBinding binding;
  private DriveProjectsAdapter adapter;
  private ArrayList<ProjectsDataInObject> projectsList;
  private BottomSheetBehavior projectsBottomSheetBehavior;
  private final SparseArray<int[]> driveRes = new SparseArray<>();
  private SharedPreferencesManager sharedPreferencesManager;

  @Override
  public View onCreateView(
      LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
    // Inflate the layout for this fragment
    binding = FragmentProjectsBinding.inflate(inflater, container, false);
    sharedPreferencesManager = new SharedPreferencesManager(requireContext());
    projectsBottomSheetBehavior = BottomSheetBehavior.from(binding.projectsBottomSheet);
    projectsBottomSheetBehavior.setState(BottomSheetBehavior.STATE_HIDDEN);
    return binding.getRoot();
  }

  @Override
  public void onViewCreated(@NonNull View view, @NonNull Bundle savedInstanceState) {
    super.onViewCreated(view, savedInstanceState);
    projectsBottomSheetBehavior.addBottomSheetCallback(dpBottomSheetCallback);
    requireView()
        .findViewById(R.id.dp_start_btn)
        .setOnClickListener(
            v ->
                Navigation.findNavController(requireView())
                    .navigate(R.id.action_projectsFragment_to_blocklyExecutingFragment));
    requireView()
        .findViewById(R.id.dp_cancel_btn)
        .setOnClickListener(
            v -> projectsBottomSheetBehavior.setState(BottomSheetBehavior.STATE_HIDDEN));

    binding.refreshLayout.setOnRefreshListener(this::showProjectsRv);
    showProjectsRv();
  }

  private void showProjectsRv() {
    binding.noProjectsLayout.setVisibility(View.GONE);
    binding.refreshLayout.setVisibility(View.VISIBLE);
    projectsList = sharedPreferencesManager.getProjectList();
    // Set Grid layout according to screen width dimension.
    int screenWidth = getResources().getDisplayMetrics().widthPixels;
    int itemWidth = getResources().getDimensionPixelSize(R.dimen.project_card_view);
    int numColumns = screenWidth / itemWidth;
    binding.projectsRv.setLayoutManager(new GridLayoutManager(requireActivity(), numColumns));
    driveRes.put(R.layout.projects_list_view, new int[] {R.id.project_name, R.id.project_date});
    setScanDeviceAdapter(
        new DriveProjectsAdapter(requireActivity(), projectsList, driveRes),
        (itemView, position) ->
            onTapProjectItem(
                projectsList.get(position).getProjectCommands(),
                projectsList.get(position).getProjectName()),
        ((itemView, position) ->
            onLongTapProjectItem(
                projectsList.get(position).getProjectName(),
                projectsList.get(position).getProjectId())));
    binding.projectsLoader.setVisibility(View.GONE);
    binding.refreshLayout.setRefreshing(false);
    binding.projectsRv.setAdapter(adapter);
    if (projectsList.isEmpty()) {
      binding.noProjectsLayout.setVisibility(View.VISIBLE);
    }
  }

  private void setScanDeviceAdapter(
      DriveProjectsAdapter adapter,
      @NonNull CommonRecyclerViewAdapter.OnItemClickListener onItemClickListener,
      CommonRecyclerViewAdapter.OnItemLongClickListener onItemLongClickListener) {
    this.adapter = adapter;
    adapter.setOnItemClickListener(onItemClickListener);
    adapter.setOnItemLongClickListener(onItemLongClickListener);
  }

  /**
   * This method is called when a project item is tapped. It performs to run project's command.
   *
   * @param fileContents
   * @param projectName
   */
  private void onTapProjectItem(String fileContents, String projectName) {
    String code = fileContents;
    for (String fun : BotFunctionUtils.botFunctionArray) {
      if (code.contains(fun)) {
        code = code.replace(fun, "Android." + fun);
      }
    }
    BlocklyExecutingFragment.finalCode = code;
    binding.dpMessage.setText(
        getString(R.string.project_file_detected, projectName.replace(".js", "")));
    projectsBottomSheetBehavior.setState(BottomSheetBehavior.STATE_EXPANDED);
  }

  /**
   * This method is triggered when a long tap is performed on a project item. It displays an
   * AlertDialog with a confirmation message to delete the project from the local list.
   *
   * @param projectName
   * @param projectId
   */
  private void onLongTapProjectItem(String projectName, String projectId) {
    AlertDialog.Builder builder = new AlertDialog.Builder(requireActivity());
    builder.setTitle("Delete this project ?").setMessage("You cannot restore this project later.");
    builder.setPositiveButton(
        "Delete",
        (dialog, id) -> {
          for (int i = projectsList.size() - 1; i >= 0; i--) {
            if (projectsList.get(i).getProjectId().equals(projectId)) {
              projectsList.remove(i);
            }
          }
          sharedPreferencesManager.setProjectLIst(projectsList);
          showProjectsRv();
        });
    builder.setNegativeButton("Cancel", (dialog, id) -> dialog.cancel());
    AlertDialog dialog = builder.create();
    dialog.show();
  }

  private BottomSheetBehavior.BottomSheetCallback dpBottomSheetCallback =
      new BottomSheetBehavior.BottomSheetCallback() {
        @Override
        public void onStateChanged(@NonNull View bottomSheet, int newState) {
          // Handle state changes here
          if (newState == BottomSheetBehavior.STATE_DRAGGING) {
            projectsBottomSheetBehavior.setState(BottomSheetBehavior.STATE_HIDDEN);
          }
          if (newState == BottomSheetBehavior.STATE_EXPANDED
              || newState == BottomSheetBehavior.STATE_HALF_EXPANDED) {
            binding.projectsLoader.setVisibility(View.GONE);
            binding.overlayView.setVisibility(View.VISIBLE);
          } else if (newState == BottomSheetBehavior.STATE_HIDDEN) {
            binding.overlayView.setVisibility(View.GONE);
          }
        }

        @Override
        public void onSlide(@NonNull View bottomSheet, float slideOffset) {
          // Handle sliding state changes here
        }
      };

  @Override
  public void onResume() {
    super.onResume();
    projectsBottomSheetBehavior.setState(BottomSheetBehavior.STATE_HIDDEN);
  }
}