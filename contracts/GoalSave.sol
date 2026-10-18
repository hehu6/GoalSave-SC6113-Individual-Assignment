// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title GoalSave - goal-based ETH savings on Sepolia
/// @notice Users create savings goals, deposit ETH, and withdraw after reaching
///         the target or the chosen deadline. Every material action emits an event.
contract GoalSave {
    enum GoalStatus {
        Active,
        Withdrawn,
        EmergencyClosed
    }

    struct Goal {
        address owner;
        string name;
        uint256 targetAmount;
        uint256 savedAmount;
        uint64 deadline;
        uint64 createdAt;
        GoalStatus status;
    }

    uint256 public constant MAX_NAME_LENGTH = 64;
    uint256 public goalCount;

    mapping(uint256 => Goal) private goals;
    mapping(address => uint256[]) private ownerGoalIds;
    bool private entered;

    error EmptyName();
    error NameTooLong();
    error InvalidTarget();
    error InvalidDeadline();
    error GoalNotFound();
    error NotGoalOwner();
    error GoalNotActive();
    error ZeroDeposit();
    error NothingToWithdraw();
    error WithdrawalLocked();
    error TransferFailed();
    error ReentrantCall();
    error DirectTransferDisabled();

    event GoalCreated(
        uint256 indexed goalId,
        address indexed owner,
        string name,
        uint256 targetAmount,
        uint64 deadline
    );
    event DepositAdded(
        uint256 indexed goalId,
        address indexed owner,
        address indexed contributor,
        uint256 amount,
        uint256 newBalance
    );
    event GoalReached(uint256 indexed goalId, address indexed owner, uint256 savedAmount);
    event GoalWithdrawn(uint256 indexed goalId, address indexed owner, uint256 amount);
    event EmergencyWithdrawal(uint256 indexed goalId, address indexed owner, uint256 amount);

    modifier existingGoal(uint256 goalId) {
        if (goalId == 0 || goalId > goalCount) revert GoalNotFound();
        _;
    }

    modifier onlyGoalOwner(uint256 goalId) {
        if (goals[goalId].owner != msg.sender) revert NotGoalOwner();
        _;
    }

    modifier nonReentrant() {
        if (entered) revert ReentrantCall();
        entered = true;
        _;
        entered = false;
    }

    /// @notice Create a new savings goal.
    function createGoal(
        string calldata name,
        uint256 targetAmount,
        uint64 deadline
    ) external returns (uint256 goalId) {
        uint256 nameLength = bytes(name).length;
        if (nameLength == 0) revert EmptyName();
        if (nameLength > MAX_NAME_LENGTH) revert NameTooLong();
        if (targetAmount == 0) revert InvalidTarget();
        if (deadline <= block.timestamp) revert InvalidDeadline();

        goalId = ++goalCount;
        goals[goalId] = Goal({
            owner: msg.sender,
            name: name,
            targetAmount: targetAmount,
            savedAmount: 0,
            deadline: deadline,
            createdAt: uint64(block.timestamp),
            status: GoalStatus.Active
        });
        ownerGoalIds[msg.sender].push(goalId);

        emit GoalCreated(goalId, msg.sender, name, targetAmount, deadline);
    }

    /// @notice Deposit ETH into an active goal. Other wallets may contribute.
    function deposit(uint256 goalId) external payable existingGoal(goalId) {
        Goal storage goal = goals[goalId];
        if (goal.status != GoalStatus.Active) revert GoalNotActive();
        if (msg.value == 0) revert ZeroDeposit();

        uint256 previousBalance = goal.savedAmount;
        goal.savedAmount = previousBalance + msg.value;

        emit DepositAdded(goalId, goal.owner, msg.sender, msg.value, goal.savedAmount);
        if (previousBalance < goal.targetAmount && goal.savedAmount >= goal.targetAmount) {
            emit GoalReached(goalId, goal.owner, goal.savedAmount);
        }
    }

    /// @notice Withdraw when the target is reached or the deadline has passed.
    function withdraw(uint256 goalId)
        external
        existingGoal(goalId)
        onlyGoalOwner(goalId)
        nonReentrant
    {
        Goal storage goal = goals[goalId];
        if (goal.status != GoalStatus.Active) revert GoalNotActive();
        if (goal.savedAmount == 0) revert NothingToWithdraw();
        if (goal.savedAmount < goal.targetAmount && block.timestamp < goal.deadline) {
            revert WithdrawalLocked();
        }

        uint256 amount = goal.savedAmount;
        goal.savedAmount = 0;
        goal.status = GoalStatus.Withdrawn;

        (bool sent, ) = payable(msg.sender).call{value: amount}("");
        if (!sent) revert TransferFailed();

        emit GoalWithdrawn(goalId, msg.sender, amount);
    }

    /// @notice Close early and return the current savings to the goal owner.
    /// @dev This explicit escape hatch is transparent because it emits a distinct event.
    function emergencyWithdraw(uint256 goalId)
        external
        existingGoal(goalId)
        onlyGoalOwner(goalId)
        nonReentrant
    {
        Goal storage goal = goals[goalId];
        if (goal.status != GoalStatus.Active) revert GoalNotActive();
        if (goal.savedAmount == 0) revert NothingToWithdraw();

        uint256 amount = goal.savedAmount;
        goal.savedAmount = 0;
        goal.status = GoalStatus.EmergencyClosed;

        (bool sent, ) = payable(msg.sender).call{value: amount}("");
        if (!sent) revert TransferFailed();

        emit EmergencyWithdrawal(goalId, msg.sender, amount);
    }

    function getGoal(uint256 goalId) external view existingGoal(goalId) returns (Goal memory) {
        return goals[goalId];
    }

    function getGoalIds(address owner) external view returns (uint256[] memory) {
        return ownerGoalIds[owner];
    }

    receive() external payable {
        revert DirectTransferDisabled();
    }

    fallback() external payable {
        revert DirectTransferDisabled();
    }
}
